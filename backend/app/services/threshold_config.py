"""
Tenant threshold configuration — Phase 1A + 1B.

get_tenant_thresholds(tenant_id) now reads from the DB (tenant_thresholds table).
Falls back to defaults if no row exists. Includes detect-only mode flag.
"""
from dataclasses import dataclass, field
from typing import Literal

from app.models.database import get_tenant_threshold_row


@dataclass
class ThresholdConfig:
    DPD_THRESHOLD: float = 0.10   # Demographic Parity Difference
    EOD_THRESHOLD: float = 0.08   # Equalized Odds Difference
    ICD_THRESHOLD: float = 0.15   # Individual Counterfactual Disparity
    CAS_THRESHOLD: float = 0.20   # Causal Attribution Score
    mode: Literal["detect_only", "detect_and_correct"] = "detect_and_correct"


def get_tenant_thresholds(tenant_id: str) -> ThresholdConfig:
    """
    Return ThresholdConfig for a tenant, loaded from DB.
    Falls back to system defaults if no custom config is set.
    """
    row = get_tenant_threshold_row(tenant_id)
    if row is None:
        return ThresholdConfig()
    return ThresholdConfig(
        DPD_THRESHOLD=row.dpd_threshold,
        EOD_THRESHOLD=row.eod_threshold,
        ICD_THRESHOLD=row.icd_threshold,
        CAS_THRESHOLD=row.cas_threshold,
        mode=row.mode,  # type: ignore[arg-type]
    )
