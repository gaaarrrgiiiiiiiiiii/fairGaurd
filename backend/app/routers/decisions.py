"""
Decisions router — POST /v1/decision

Phase 2 pipeline:
  1. Auth (H1 — from Phase 1)
  2. Fast-path if no protected attrs
  3. [H2] CPU-bound bias + causal run in thread-pool executor (truly parallel)
  4. Threshold evaluation
  5. [C3] apply_correction_fast() — counterfactual only, no LLM, <1ms
  6. [H2] Audit log persisted async (non-blocking)
  7. [C3] LLM explanation fired as BackgroundTask — runs AFTER HTTP response sent
  8. Graceful degradation on any failure
"""
import asyncio
import logging
import time
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.jwt_handler import verify_token, DEV_MODE
from app.models.database import create_audit_log_async, update_audit_explanation_async
from app.models.schemas import DecisionRequest, DecisionResponse
from app.services.bias_detector import bias_detector
from app.services.causal_engine import causal_engine
from app.services.corrector import corrector
from app.services.threshold_config import get_tenant_thresholds
from app.routers.stream import publish_event

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)
limiter = Limiter(key_func=get_remote_address)


# ---------------------------------------------------------------------------
# Background task — runs AFTER response is already sent to caller
# ---------------------------------------------------------------------------
async def _update_explanation_bg(
    audit_id: str,
    features: dict,
    original_decision: str,
    corrected_decision: str,
    protected_attrs: list,
) -> None:
    """C3: Fire-and-forget — generates LLM explanation and patches audit log."""
    try:
        explanation = await corrector.generate_explanation_async(
            features=features,
            original_decision=original_decision,
            corrected_decision=corrected_decision,
            protected_attributes=protected_attrs,
        )
        await update_audit_explanation_async(audit_id, explanation)
        logger.info("Background explanation updated for audit %s", audit_id[:8])
    except Exception as exc:
        logger.warning("Background explanation task failed: %s", exc)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("/decision", response_model=DecisionResponse)
@limiter.limit("100/minute")
async def evaluate_decision(
    request: Request,
    body: DecisionRequest,
    background_tasks: BackgroundTasks,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    """
    Evaluate an ML model decision for demographic bias.

    Phase 2 latency targets:
      • Bias + causal (CPU): run in parallel thread-pool executors
      • Counterfactual:      sync, in-process (<1 ms)
      • Audit log write:     async (thread-pool, non-blocking)
      • LLM explanation:     BackgroundTask — fires after response sent
    """
    t0 = time.perf_counter()

    # --- Auth (H1) ---
    raw_token = credentials.credentials if credentials else None
    tenant_id = verify_token(raw_token)

    if tenant_id is None:
        if DEV_MODE:
            tenant_id = "tenant_local_dev"
            logger.warning(
                "DEV_MODE: unauthenticated request accepted as tenant_local_dev. "
                "Set FAIRGUARD_DEV_MODE=false before deploying."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Provide a valid Bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    thresholds    = get_tenant_thresholds(tenant_id)
    protected_attrs = body.protected_attributes or []

    # --- Fast path: no protected attributes ---
    if not protected_attrs:
        audit_id = await create_audit_log_async(
            tenant_id=tenant_id,
            original_decision=body.model_output,
            corrected_decision=body.model_output,
            bias_scores={},
            explanation="Passed through — no protected attributes provided.",
            protected_attributes=[],
        )
        return DecisionResponse(
            original_decision=body.model_output,
            corrected_decision=body.model_output,
            bias_detected=False,
            explanation="Passed through. No protected attributes evaluated.",
            audit_id=audit_id,
        )

    # --- Main pipeline ---
    try:
        loop = asyncio.get_event_loop()

        # Stage 1+2: [H2] CPU-bound work — truly parallel in separate threads
        bias_scores, causal_paths = await asyncio.gather(
            loop.run_in_executor(
                None,
                bias_detector.evaluate,
                body.applicant_features, body.model_output, protected_attrs,
            ),
            loop.run_in_executor(
                None,
                causal_engine.discover_paths,
                body.applicant_features, protected_attrs,
            ),
        )

        t_bias = time.perf_counter()
        logger.debug("Bias+causal computed in %.1f ms", (t_bias - t0) * 1000)

        # Stage 3: threshold evaluation
        dpd = bias_scores.get("DPD", 0.0)
        eod = bias_scores.get("EOD", 0.0)
        icd = bias_scores.get("ICD", 0.0)
        cas = bias_scores.get("CAS", 0.0)

        bias_detected         = dpd > thresholds.DPD_THRESHOLD or eod > thresholds.EOD_THRESHOLD
        intervention_required = icd > thresholds.ICD_THRESHOLD or cas > thresholds.CAS_THRESHOLD
        if intervention_required:
            bias_detected = True

        explanation        = "No statistically significant bias detected."
        corrected_decision = body.model_output

        # Stage 4: [C3] Fast correction — no LLM on hot path
        if intervention_required:
            corrected_decision, explanation = corrector.apply_correction_fast(
                features=body.applicant_features,
                model_output=body.model_output,
                protected_attributes=protected_attrs,
                bias_scores=bias_scores,
            )
        elif bias_detected:
            explanation = (
                "Bias alert triggered on population metrics, "
                "but individual intervention threshold not met."
            )

        # Stage 5: [H2] Persist audit log asynchronously (non-blocking)
        audit_id = await create_audit_log_async(
            tenant_id=tenant_id,
            original_decision=body.model_output,
            corrected_decision=corrected_decision,
            bias_scores=bias_scores,
            explanation=explanation,
            protected_attributes=protected_attrs,
        )

        # Stage 6a: [Phase 3] Publish to SSE clients immediately
        publish_event(tenant_id, {
            "audit_id":           audit_id,
            "original_decision":  body.model_output,
            "corrected_decision": corrected_decision,
            "bias_detected":      bias_detected,
            "bias_scores":        bias_scores,
            "explanation":        explanation,
            "protected_attributes": protected_attrs,
        })

        # Stage 6b: [C3] Fire-and-forget LLM explanation — runs after response sent
        if intervention_required:
            background_tasks.add_task(
                _update_explanation_bg,
                audit_id=audit_id,
                features=body.applicant_features,
                original_decision=body.model_output.get("decision", ""),
                corrected_decision=corrected_decision.get("decision", ""),
                protected_attrs=protected_attrs,
            )

        t_total = time.perf_counter()
        logger.info(
            "Decision [%s] tenant=%s bias=%s intervention=%s total=%.1fms",
            audit_id[:8], tenant_id, bias_detected, intervention_required,
            (t_total - t0) * 1000,
        )

        return DecisionResponse(
            original_decision=body.model_output,
            corrected_decision=corrected_decision,
            bias_detected=bias_detected,
            explanation=explanation,
            audit_id=audit_id,
        )

    except Exception as exc:
        # Graceful degradation — never crash the caller's system
        logger.error("Pipeline failure: %s", exc, exc_info=True)

        try:
            audit_id = await create_audit_log_async(
                tenant_id=tenant_id,
                original_decision=body.model_output,
                corrected_decision=body.model_output,
                bias_scores={},
                explanation=f"SYSTEM_ERROR: Pipeline degraded gracefully. {exc}",
                protected_attributes=protected_attrs,
            )
        except Exception:
            audit_id = None

        return DecisionResponse(
            original_decision=body.model_output,
            corrected_decision=body.model_output,
            bias_detected=False,
            explanation="Safety Passthrough: ML engine was unable to evaluate request.",
            audit_id=audit_id,
        )
