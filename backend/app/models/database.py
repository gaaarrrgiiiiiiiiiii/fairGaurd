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
    Float,
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
_DB_URL_RAW = os.environ.get("DATABASE_URL", "sqlite:///./fairguard.db")

if _DB_URL_RAW.startswith("sqlite:///"):
    # Resolve path — support both relative (./foo.db) and absolute (/data/foo.db)
    _sqlite_path = _DB_URL_RAW[len("sqlite:///"):]
    if not os.path.isabs(_sqlite_path):
        # Relative path: anchor it to /app/data inside Docker, or the backend root locally
        _sqlite_path = _sqlite_path.lstrip("./")
        # /app/data/<file> inside Docker; backend/ locally via DATABASE_URL env override
        _data_dir = os.environ.get("FAIRGUARD_DATA_DIR",
                       os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
        _sqlite_path = os.path.join(_data_dir, _sqlite_path)
    # Always create parent directory — covers first boot in any environment
    _db_dir = os.path.dirname(_sqlite_path)
    os.makedirs(_db_dir, exist_ok=True)
    DATABASE_URL     = f"sqlite:///{_sqlite_path}"
    DATABASE_URL_RAW = _sqlite_path          # used by drift.py (sqlite3 import)
else:
    DATABASE_URL     = _DB_URL_RAW
    DATABASE_URL_RAW = _DB_URL_RAW

logger.info("Database: %s", DATABASE_URL)

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
    # Phase 1C — immutable hash chain (EU AI Act Art. 12)
    prev_hash           = Column(String(64), nullable=True)
    record_hash         = Column(String(64), nullable=True)


class TenantThreshold(Base):
    """Per-tenant configurable thresholds + operation mode (Phase 1A/1B)."""
    __tablename__ = "tenant_thresholds"

    tenant_id           = Column(String, primary_key=True)
    dpd_threshold       = Column(Float, default=0.10, nullable=False)
    eod_threshold       = Column(Float, default=0.08, nullable=False)
    icd_threshold       = Column(Float, default=0.15, nullable=False)
    cas_threshold       = Column(Float, default=0.20, nullable=False)
    mode                = Column(String, default="detect_and_correct", nullable=False)
    updated_at          = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Webhook(Base):
    """Registered webhook endpoints for a tenant (Phase 2 — Gap 4)."""
    __tablename__ = "webhooks"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id  = Column(String, nullable=False, index=True)
    url        = Column(Text, nullable=False)
    events     = Column(Text, nullable=False, default="bias.detected,drift.detected")
    secret     = Column(String, nullable=True)   # HMAC-SHA256 signing secret
    active     = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

import hashlib as _hashlib

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

    orig_dec  = original_decision.get("decision",  "")
    corr_dec  = corrected_decision.get("decision", "")
    correction_applied = (orig_dec != corr_dec)

    db = SessionLocal()
    try:
        # Phase 1C — fetch previous hash for chain integrity
        last = (
            db.query(AuditLog)
            .filter(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.timestamp.desc())
            .first()
        )
        prev_hash = last.record_hash if last and last.record_hash else "0" * 64

        # Build canonical content string and hash it
        content = json.dumps({
            "id": audit_id, "tenant_id": tenant_id,
            "original_decision": original_decision,
            "corrected_decision": corrected_decision,
            "bias_scores": bias_scores,
            "protected_attributes": protected_attributes,
            "correction_applied": correction_applied,
        }, sort_keys=True)
        record_hash = _hashlib.sha256((prev_hash + content).encode()).hexdigest()

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
            prev_hash            = prev_hash,
            record_hash          = record_hash,
        )
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


# ---------------------------------------------------------------------------
# Phase 1A/1B — Tenant threshold CRUD
# ---------------------------------------------------------------------------

def get_tenant_threshold_row(tenant_id: str) -> Optional["TenantThreshold"]:
    """Return the DB row or None if no custom config exists."""
    db = SessionLocal()
    try:
        return db.query(TenantThreshold).filter(TenantThreshold.tenant_id == tenant_id).first()
    finally:
        db.close()


def upsert_tenant_thresholds(
    tenant_id: str,
    dpd: float,
    eod: float,
    icd: float,
    cas: float,
    mode: str,
) -> None:
    """Insert or update threshold config for a tenant."""
    db = SessionLocal()
    try:
        row = db.query(TenantThreshold).filter(TenantThreshold.tenant_id == tenant_id).first()
        if row:
            row.dpd_threshold = dpd
            row.eod_threshold = eod
            row.icd_threshold = icd
            row.cas_threshold = cas
            row.mode = mode
            row.updated_at = datetime.datetime.utcnow()
        else:
            row = TenantThreshold(
                tenant_id=tenant_id, dpd_threshold=dpd,
                eod_threshold=eod, icd_threshold=icd,
                cas_threshold=cas, mode=mode,
            )
            db.add(row)
        db.commit()
        logger.debug("Thresholds upserted for tenant %s", tenant_id)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to upsert thresholds: %s", exc)
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Phase 1C — Audit chain verification
# ---------------------------------------------------------------------------

def verify_audit_chain(tenant_id: str) -> Dict[str, Any]:
    """Walk the hash chain; return integrity status."""
    db = SessionLocal()
    try:
        rows = (
            db.query(AuditLog)
            .filter(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.timestamp.asc())
            .all()
        )
    finally:
        db.close()

    if not rows:
        return {"valid": True, "records_checked": 0, "first_violation": None}

    prev = "0" * 64
    for i, row in enumerate(rows):
        if row.record_hash is None:
            # Legacy record before Phase 1C — skip
            prev = row.record_hash or prev
            continue
        content = json.dumps({
            "id": row.id, "tenant_id": row.tenant_id,
            "original_decision": json.loads(row.original_decision),
            "corrected_decision": json.loads(row.corrected_decision),
            "bias_scores": json.loads(row.bias_scores or "{}"),
            "protected_attributes": json.loads(row.protected_attributes or "[]"),
            "correction_applied": row.correction_applied,
        }, sort_keys=True)
        expected = _hashlib.sha256((prev + content).encode()).hexdigest()
        if expected != row.record_hash:
            return {
                "valid": False,
                "records_checked": i + 1,
                "first_violation": row.id,
            }
        prev = row.record_hash

    return {"valid": True, "records_checked": len(rows), "first_violation": None}


# ---------------------------------------------------------------------------
# Phase 2 — Webhook CRUD (Gap 4)
# ---------------------------------------------------------------------------

def list_webhooks(tenant_id: str) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.query(Webhook).filter(Webhook.tenant_id == tenant_id).all()
        return [
            {"id": r.id, "url": r.url, "events": r.events,
             "active": r.active, "created_at": r.created_at.isoformat()}
            for r in rows
        ]
    finally:
        db.close()


def create_webhook(tenant_id: str, url: str, events: str, secret: Optional[str]) -> str:
    db = SessionLocal()
    try:
        row = Webhook(tenant_id=tenant_id, url=url, events=events, secret=secret)
        db.add(row)
        db.commit()
        return row.id
    except Exception as exc:
        db.rollback()
        logger.error("Failed to create webhook: %s", exc)
        raise
    finally:
        db.close()


def delete_webhook(tenant_id: str, webhook_id: str) -> bool:
    db = SessionLocal()
    try:
        row = db.query(Webhook).filter(
            Webhook.id == webhook_id, Webhook.tenant_id == tenant_id
        ).first()
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True
    except Exception as exc:
        db.rollback()
        logger.error("Failed to delete webhook: %s", exc)
        raise
    finally:
        db.close()


def get_webhooks_for_event(tenant_id: str, event_type: str) -> List[Dict[str, Any]]:
    """Return active webhooks for a tenant that subscribe to event_type."""
    db = SessionLocal()
    try:
        rows = db.query(Webhook).filter(
            Webhook.tenant_id == tenant_id, Webhook.active == True  # noqa: E712
        ).all()
        return [
            {"id": r.id, "url": r.url, "secret": r.secret}
            for r in rows
            if event_type in r.events.split(",")
        ]
    finally:
        db.close()

