"""
Decisions router — POST /v1/decision  |  POST /v1/decisions/batch

Pipeline:
  1. RBAC auth (any authenticated role)
  2. Fast-path if no protected attrs
  3. [H2] CPU-bound bias + causal in thread-pool (parallel)
  4. Threshold evaluation + detect-only mode check
  5. [C3] Fast correction
  6. Async audit log + SSE publish
  7. LLM explanation as BackgroundTask
  8. Graceful degradation
"""
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.rbac import TenantContext, any_authenticated, auditor_or_admin
from app.models.database import (
    create_audit_log_async, update_audit_explanation_async, get_domain_analytics
)
from app.models.schemas import DecisionRequest, DecisionResponse
from app.services.bias_detector import bias_detector
from app.services.causal_engine import causal_engine
from app.services.domain_registry import list_domains
from app.services.corrector import corrector
from app.services.threshold_config import get_tenant_thresholds
from app.services.webhook_dispatcher import dispatch_event
from app.routers.stream import publish_event

logger = logging.getLogger(__name__)
router = APIRouter()
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
    ctx: TenantContext = Depends(any_authenticated),
):
    t0 = time.perf_counter()
    tenant_id = ctx.tenant_id

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
            domain=body.domain,
        )
        return DecisionResponse(
            original_decision=body.model_output,
            corrected_decision=body.model_output,
            bias_detected=False,
            explanation="Passed through. No protected attributes evaluated.",
            audit_id=audit_id,
            domain=body.domain,
            bias_scores={},
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

        # Stage 4: [C3/1B] Fast correction — skipped in detect_only mode
        detect_only = thresholds.mode == "detect_only"

        if detect_only and (bias_detected or intervention_required):
            explanation = (
                "[DETECT-ONLY MODE] Bias detected but no correction applied per tenant policy. "
                f"DPD={dpd:.3f} EOD={eod:.3f} ICD={icd:.3f} CAS={cas:.3f}"
            )
        elif intervention_required:
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
            domain=body.domain,
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

        # Webhooks — fire as background tasks (never blocks response)
        if bias_detected:
            background_tasks.add_task(
                dispatch_event, tenant_id, "bias.detected",
                {"audit_id": audit_id, "bias_scores": bias_scores,
                 "protected_attributes": protected_attrs},
            )
        if intervention_required and not detect_only:
            background_tasks.add_task(
                dispatch_event, tenant_id, "correction.applied",
                {"audit_id": audit_id,
                 "original": body.model_output.get("decision"),
                 "corrected": corrected_decision.get("decision")},
            )

        # Stage 6b: [C3] Fire-and-forget LLM explanation — only when correction was actually made
        if intervention_required and not detect_only:
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
            domain=body.domain,
            bias_scores=bias_scores,
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
                domain=body.domain,
            )
        except Exception:
            audit_id = None

        return DecisionResponse(
            original_decision=body.model_output,
            corrected_decision=body.model_output,
            bias_detected=False,
            explanation="Safety Passthrough: ML engine was unable to evaluate request.",
            audit_id=audit_id,
            bias_scores={},
        )


# ---------------------------------------------------------------------------
# Gap 6 — Batch endpoint
# ---------------------------------------------------------------------------

class BatchDecisionRequest(BaseModel):
    decisions: List[DecisionRequest] = Field(
        ..., min_length=1, max_length=50,
        description="Up to 50 decision items to evaluate concurrently.",
    )


class BatchDecisionResponse(BaseModel):
    results: List[DecisionResponse]
    total: int
    biased: int
    corrected: int
    detect_only_flagged: int


async def _run_single(
    item: DecisionRequest,
    tenant_id: str,
    background_tasks: BackgroundTasks,
) -> DecisionResponse:
    """Run the full bias pipeline for one decision; used by both single + batch."""
    t0 = time.perf_counter()
    thresholds    = get_tenant_thresholds(tenant_id)
    protected_attrs = item.protected_attributes or []

    if not protected_attrs:
        audit_id = await create_audit_log_async(
            tenant_id=tenant_id,
            original_decision=item.model_output,
            corrected_decision=item.model_output,
            bias_scores={},
            explanation="Passed through — no protected attributes provided.",
            protected_attributes=[],
            domain=item.domain,
        )
        return DecisionResponse(
            original_decision=item.model_output,
            corrected_decision=item.model_output,
            bias_detected=False,
            explanation="Passed through. No protected attributes evaluated.",
            audit_id=audit_id,
            domain=item.domain,
            bias_scores={},
        )

    try:
        loop = asyncio.get_event_loop()
        bias_scores, causal_paths = await asyncio.gather(
            loop.run_in_executor(None, bias_detector.evaluate,
                item.applicant_features, item.model_output, protected_attrs),
            loop.run_in_executor(None, causal_engine.discover_paths,
                item.applicant_features, protected_attrs),
        )

        dpd = bias_scores.get("DPD", 0.0)
        eod = bias_scores.get("EOD", 0.0)
        icd = bias_scores.get("ICD", 0.0)
        cas = bias_scores.get("CAS", 0.0)

        bias_detected         = dpd > thresholds.DPD_THRESHOLD or eod > thresholds.EOD_THRESHOLD
        intervention_required = icd > thresholds.ICD_THRESHOLD or cas > thresholds.CAS_THRESHOLD
        if intervention_required:
            bias_detected = True

        detect_only        = thresholds.mode == "detect_only"
        explanation        = "No statistically significant bias detected."
        corrected_decision = item.model_output

        if detect_only and (bias_detected or intervention_required):
            explanation = (
                f"[DETECT-ONLY] Bias detected. DPD={dpd:.3f} EOD={eod:.3f} "
                f"ICD={icd:.3f} CAS={cas:.3f}"
            )
        elif intervention_required:
            corrected_decision, explanation = corrector.apply_correction_fast(
                features=item.applicant_features,
                model_output=item.model_output,
                protected_attributes=protected_attrs,
                bias_scores=bias_scores,
            )
        elif bias_detected:
            explanation = "Bias alert on population metrics; individual threshold not met."

        audit_id = await create_audit_log_async(
            tenant_id=tenant_id,
            original_decision=item.model_output,
            corrected_decision=corrected_decision,
            bias_scores=bias_scores,
            explanation=explanation,
            protected_attributes=protected_attrs,
            domain=item.domain,
        )
        publish_event(tenant_id, {
            "audit_id": audit_id, "original_decision": item.model_output,
            "corrected_decision": corrected_decision, "bias_detected": bias_detected,
        })
        if intervention_required and not detect_only:
            background_tasks.add_task(
                _update_explanation_bg, audit_id=audit_id,
                features=item.applicant_features,
                original_decision=item.model_output.get("decision", ""),
                corrected_decision=corrected_decision.get("decision", ""),
                protected_attrs=protected_attrs,
            )
        return DecisionResponse(
            original_decision=item.model_output,
            corrected_decision=corrected_decision,
            bias_detected=bias_detected,
            explanation=explanation,
            audit_id=audit_id,
            domain=item.domain,
            bias_scores=bias_scores,
        )
    except Exception as exc:
        logger.error("Batch item pipeline failure: %s", exc)
        return DecisionResponse(
            original_decision=item.model_output,
            corrected_decision=item.model_output,
            bias_detected=False,
            explanation="Safety Passthrough: pipeline error.",
            bias_scores={},
        )


@router.post("/decisions/batch", response_model=BatchDecisionResponse)
@limiter.limit("20/minute")
async def evaluate_batch(
    request: Request,
    body: BatchDecisionRequest,
    background_tasks: BackgroundTasks,
    ctx: TenantContext = Depends(any_authenticated),
):
    """
    Evaluate up to 50 decisions concurrently.
    Critical for enterprise retroactive compliance audits on historical datasets.
    All items run in parallel via asyncio.gather().
    """
    results = await asyncio.gather(
        *[_run_single(item, ctx.tenant_id, background_tasks)
          for item in body.decisions]
    )
    return BatchDecisionResponse(
        results=list(results),
        total=len(results),
        biased=sum(1 for r in results if r.bias_detected),
        corrected=sum(
            1 for r in results
            if r.bias_detected and r.original_decision != r.corrected_decision
        ),
        detect_only_flagged=sum(
            1 for r in results
            if r.explanation and "DETECT-ONLY" in (r.explanation or "")
        ),
    )


# ---------------------------------------------------------------------------
# Gap 2 — Multi-domain analytics endpoint
# ---------------------------------------------------------------------------

@router.get("/decisions/domains", summary="Per-domain bias analytics")
async def get_domain_breakdown(
    ctx: TenantContext = Depends(auditor_or_admin),
):
    """
    Return per-domain breakdown of decisions, interventions, and compliance rate.
    Requires auditor or admin role.

    Example response:
      [{"domain": "credit", "total_decisions": 120, "interventions": 8, "compliance_rate": 93.33},
       {"domain": "hiring", "total_decisions": 55,  "interventions": 2, "compliance_rate": 96.36}]
    """
    return await asyncio.get_event_loop().run_in_executor(
        None, get_domain_analytics, ctx.tenant_id
    )


# ---------------------------------------------------------------------------
# Phase 4A — Domain registry listing endpoint
# ---------------------------------------------------------------------------

@router.get("/domains", summary="List all supported bias-detection domains")
async def list_supported_domains():
    """
    Returns the registry of domains FairGuard can evaluate.
    Includes protected attributes, decision vocabulary, and description.

    No auth required — public discovery endpoint.
    """
    return list_domains()
