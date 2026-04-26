"""
Database layer — SQLAlchemy ORM models and session management.

Uses SQLite for development (zero-config). Switch DATABASE_URL in .env
to postgresql://... for production.

Compliance-rate calculation is fixed:
  An "intervention" is any record where corrected_decision differs from
  original_decision (i.e. bias was detected AND a correction was applied).
  Records where no correction was made are NOT counted as interventions,
  even if an explanation is present.
"""
import asyncio
import datetime
import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    Text,
    create_engine,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engine setup
# ---------------------------------------------------------------------------
_DB_FILE = os.environ.get("DATABASE_URL", "sqlite:///./fairguard.db")

# Resolve relative sqlite path to be inside the backend directory
if _DB_FILE.startswith("sqlite:///./"):
    _db_filename = _DB_FILE.replace("sqlite:///./", "")
    _db_dir = os.path.dirname(os.path.abspath(__file__))
    # Walk up to backend/ root
    _backend_root = os.path.abspath(os.path.join(_db_dir, "../.."))
    _db_abs = os.path.join(_backend_root, _db_filename)
    DATABASE_URL = f"sqlite:///{_db_abs}"
else:
    DATABASE_URL = _DB_FILE

# SQLite raw path for legacy code that uses sqlite3 directly
_sqlite_raw = DATABASE_URL.replace("sqlite:///", "")
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL_RAW = _sqlite_raw  # used by drift.py (sqlite3 import)
else:
    DATABASE_URL_RAW = DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id                  = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id           = Column(String, nullable=False, index=True)
    timestamp           = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    original_decision   = Column(Text, nullable=False)
    corrected_decision  = Column(Text, nullable=False)
    bias_scores         = Column(Text, nullable=True)
    explanation         = Column(Text, nullable=True)
    protected_attributes= Column(Text, nullable=True)
    correction_applied  = Column(Boolean, default=False, nullable=False)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised at %s", DATABASE_URL)


def get_db() -> Session:
    """FastAPI dependency — yields a DB session, closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_audit_log(
    tenant_id: str,
    original_decision: Dict[str, Any],
    corrected_decision: Dict[str, Any],
    bias_scores: Dict[str, float],
    explanation: str,
    protected_attributes: List[str],
) -> str:
    """
    Persist a decision audit record.

    Returns the new audit ID (UUID string).
    `correction_applied` is True only when the corrected decision differs
    from the original — this is used for accurate compliance-rate calculations.
    """
    audit_id = str(uuid.uuid4())

    # Determine whether a real correction was applied
    orig_dec  = original_decision.get("decision",  "")
    corr_dec  = corrected_decision.get("decision", "")
    correction_applied = (orig_dec != corr_dec)

    record = AuditLog(
        id                   = audit_id,
        tenant_id            = tenant_id,
        timestamp            = datetime.datetime.utcnow(),
        original_decision    = json.dumps(original_decision),
        corrected_decision   = json.dumps(corrected_decision),
        bias_scores          = json.dumps(bias_scores),
        explanation          = explanation,
        protected_attributes = json.dumps(protected_attributes),
        correction_applied   = correction_applied,
    )

    db = SessionLocal()
    try:
        db.add(record)
        db.commit()
        logger.debug("Audit log created: %s (correction=%s)", audit_id, correction_applied)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to create audit log: %s", exc, exc_info=True)
        raise
    finally:
        db.close()

    return audit_id


def get_tenant_analytics(tenant_id: str) -> Dict[str, Any]:
    """
    Return aggregate statistics for a tenant.

    compliance_rate = % of decisions that DID NOT require a correction.
    """
    db = SessionLocal()
    try:
        total = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id).count()
        interventions = (
            db.query(AuditLog)
            .filter(
                AuditLog.tenant_id == tenant_id,
                AuditLog.correction_applied == True,   # noqa: E712
            )
            .count()
        )
    finally:
        db.close()

    compliance_rate = (
        100.0
        if total == 0
        else round(100.0 * (total - interventions) / total, 2)
    )

    return {
        "total_decisions": total,
        "interventions": interventions,
        "compliance_rate": compliance_rate,
    }


def get_recent_audit_logs(
    tenant_id: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Return the most recent audit log entries for a tenant (newest first)."""
    db = SessionLocal()
    try:
        rows = (
            db.query(AuditLog)
            .filter(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id":                  r.id,
                "tenant_id":           r.tenant_id,
                "timestamp":           r.timestamp.isoformat(),
                "original_decision":   json.loads(r.original_decision),
                "corrected_decision":  json.loads(r.corrected_decision),
                "bias_scores":         json.loads(r.bias_scores or "{}"),
                "explanation":         r.explanation,
                "protected_attributes":json.loads(r.protected_attributes or "[]"),
                "correction_applied":  r.correction_applied,
            }
            for r in rows
        ]
    finally:
        db.close()


# ---------------------------------------------------------------------------
# H2 — Background update (for fire-and-forget LLM explanation)
# ---------------------------------------------------------------------------

def update_audit_explanation(audit_id: str, explanation: str) -> None:
    """
    Overwrite the explanation field of an existing audit record.
    Called from a background task after the async LLM response arrives.
    """
    db = SessionLocal()
    try:
        record = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
        if record:
            record.explanation = explanation
            db.commit()
            logger.debug("Audit log %s explanation updated.", audit_id[:8])
        else:
            logger.warning("update_audit_explanation: audit_id %s not found.", audit_id)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to update audit explanation: %s", exc, exc_info=True)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# H2 — Async wrappers (run sync ORM in thread pool — never blocks event loop)
# ---------------------------------------------------------------------------

async def create_audit_log_async(
    tenant_id: str,
    original_decision: Dict[str, Any],
    corrected_decision: Dict[str, Any],
    bias_scores: Dict[str, float],
    explanation: str,
    protected_attributes: List[str],
) -> str:
    """Async wrapper — runs create_audit_log in a thread-pool executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        create_audit_log,
        tenant_id, original_decision, corrected_decision,
        bias_scores, explanation, protected_attributes,
    )


async def update_audit_explanation_async(audit_id: str, explanation: str) -> None:
    """Async wrapper — runs update_audit_explanation in a thread-pool executor."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, update_audit_explanation, audit_id, explanation)
