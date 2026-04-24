"""
Decisions router — POST /v1/decision

Core bias evaluation pipeline:
  1. Authenticate tenant (JWT or raw API key)
  2. Fast-path if no protected attributes
  3. Parallel: ICD metrics + causal path discovery
  4. Threshold evaluation → bias_detected / intervention_required
  5. Correction (if needed) via counterfactual engine + LLM explanation
  6. Audit log persistence
  7. Graceful degradation on any pipeline failure
"""
import asyncio
import logging
import time
from typing import Optional

from fastapi import APIRouter, Request, Security, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.jwt_handler import verify_token
from app.models.database import create_audit_log
from app.models.schemas import DecisionRequest, DecisionResponse
from app.services.bias_detector import bias_detector
from app.services.causal_engine import causal_engine
from app.services.corrector import corrector
from app.services.threshold_config import get_tenant_thresholds

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)
limiter = Limiter(key_func=get_remote_address)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("/decision", response_model=DecisionResponse)
@limiter.limit("100/minute")
async def evaluate_decision(
    request: Request,
    body: DecisionRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    """
    Evaluate an ML model decision for demographic bias.

    Returns the original decision, an (optionally corrected) decision,
    bias signals, an LLM-generated explanation, and an immutable audit ID.
    """
    # --- Auth ---
    raw_token = credentials.credentials if credentials else None
    tenant_id = verify_token(raw_token)
    if tenant_id is None:
        # Hackathon / dev convenience: fall back to a local dev tenant
        # rather than hard-failing so the demo works without a token.
        tenant_id = "tenant_local_dev"

    thresholds = get_tenant_thresholds(tenant_id)
    protected_attrs = body.protected_attributes or []

    # --- Fast path: no protected attributes ---
    if not protected_attrs:
        audit_id = create_audit_log(
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

    # --- Main pipeline (with graceful degradation) ---
    try:
        # Stage 1 & 2: run in parallel for speed
        async def _get_bias_metrics():
            await asyncio.sleep(0)   # yield to event loop
            return bias_detector.evaluate(
                body.applicant_features, body.model_output, protected_attrs
            )

        async def _get_causal_paths():
            await asyncio.sleep(0)
            return causal_engine.discover_paths(
                body.applicant_features, protected_attrs
            )

        bias_scores, causal_paths = await asyncio.gather(
            _get_bias_metrics(), _get_causal_paths()
        )

        # Stage 3: threshold evaluation
        bias_detected        = False
        intervention_required = False

        dpd = bias_scores.get("DPD", 0.0)
        eod = bias_scores.get("EOD", 0.0)
        icd = bias_scores.get("ICD", 0.0)
        cas = bias_scores.get("CAS", 0.0)

        if dpd > thresholds.DPD_THRESHOLD or eod > thresholds.EOD_THRESHOLD:
            bias_detected = True

        if icd > thresholds.ICD_THRESHOLD or cas > thresholds.CAS_THRESHOLD:
            bias_detected = True
            intervention_required = True

        explanation       = "No statistically significant bias detected."
        corrected_decision = body.model_output

        # Stage 4: correction
        if intervention_required:
            corrected_decision, explanation = corrector.apply_correction(
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

        # Stage 5: persist audit
        audit_id = create_audit_log(
            tenant_id=tenant_id,
            original_decision=body.model_output,
            corrected_decision=corrected_decision,
            bias_scores=bias_scores,
            explanation=explanation,
            protected_attributes=protected_attrs,
        )

        logger.info(
            "Decision [%s] tenant=%s bias=%s intervention=%s",
            audit_id[:8], tenant_id, bias_detected, intervention_required,
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
        logger.error("ML Pipeline failure: %s", exc, exc_info=True)

        audit_id = create_audit_log(
            tenant_id=tenant_id,
            original_decision=body.model_output,
            corrected_decision=body.model_output,
            bias_scores={},
            explanation=f"SYSTEM_ERROR: Pipeline degraded gracefully. {exc}",
            protected_attributes=protected_attrs,
        )

        return DecisionResponse(
            original_decision=body.model_output,
            corrected_decision=body.model_output,
            bias_detected=False,
            explanation="Safety Passthrough: ML engine was unable to evaluate request.",
            audit_id=audit_id,
        )
