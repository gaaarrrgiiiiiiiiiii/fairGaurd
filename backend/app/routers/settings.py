"""
Settings router — Phase 1A/1B/1C.

Endpoints:
  GET  /v1/settings/thresholds          — get current threshold config
  PUT  /v1/settings/thresholds          — update thresholds + mode
  GET  /v1/audit/verify                 — verify hash-chain integrity
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.rbac import TenantContext, admin_only, auditor_or_admin
from app.models.database import (
    get_tenant_threshold_row,
    upsert_tenant_thresholds,
    verify_audit_chain,
)
from app.services.threshold_config import ThresholdConfig

router = APIRouter()


# Auth handled by RBAC dependency — no manual dep needed


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ThresholdRequest(BaseModel):
    dpd_threshold: float = Field(default=0.10, ge=0.0, le=1.0, description="Demographic Parity Difference alert threshold")
    eod_threshold: float = Field(default=0.08, ge=0.0, le=1.0, description="Equalized Odds Difference alert threshold")
    icd_threshold: float = Field(default=0.15, ge=0.0, le=1.0, description="Individual Counterfactual Disparity threshold")
    cas_threshold: float = Field(default=0.20, ge=0.0, le=1.0, description="Causal Attribution Score threshold")
    mode: Literal["detect_only", "detect_and_correct"] = Field(
        default="detect_and_correct",
        description="detect_only: log bias but never modify decisions. detect_and_correct: apply corrections."
    )


class ThresholdResponse(BaseModel):
    tenant_id: str
    dpd_threshold: float
    eod_threshold: float
    icd_threshold: float
    cas_threshold: float
    mode: str
    is_custom: bool


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/thresholds", response_model=ThresholdResponse, summary="Get tenant threshold config")
def get_thresholds(ctx: TenantContext = Depends(auditor_or_admin)):
    tenant_id = ctx.tenant_id
    row = get_tenant_threshold_row(tenant_id)
    defaults = ThresholdConfig()
    if row:
        return ThresholdResponse(
            tenant_id=tenant_id,
            dpd_threshold=row.dpd_threshold,
            eod_threshold=row.eod_threshold,
            icd_threshold=row.icd_threshold,
            cas_threshold=row.cas_threshold,
            mode=row.mode,
            is_custom=True,
        )
    return ThresholdResponse(
        tenant_id=tenant_id,
        dpd_threshold=defaults.DPD_THRESHOLD,
        eod_threshold=defaults.EOD_THRESHOLD,
        icd_threshold=defaults.ICD_THRESHOLD,
        cas_threshold=defaults.CAS_THRESHOLD,
        mode=defaults.mode,
        is_custom=False,
    )


@router.put("/thresholds", response_model=ThresholdResponse, summary="Update tenant threshold config")
def update_thresholds(
    body: ThresholdRequest,
    ctx: TenantContext = Depends(admin_only),
):
    tenant_id = ctx.tenant_id
    upsert_tenant_thresholds(
        tenant_id=tenant_id,
        dpd=body.dpd_threshold,
        eod=body.eod_threshold,
        icd=body.icd_threshold,
        cas=body.cas_threshold,
        mode=body.mode,
    )
    return ThresholdResponse(
        tenant_id=tenant_id,
        dpd_threshold=body.dpd_threshold,
        eod_threshold=body.eod_threshold,
        icd_threshold=body.icd_threshold,
        cas_threshold=body.cas_threshold,
        mode=body.mode,
        is_custom=True,
    )
