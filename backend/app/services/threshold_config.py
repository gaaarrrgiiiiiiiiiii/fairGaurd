import typing

# In a production environment, this would be fetched from a database per tenant.
# For Phase 1 & 2, we load defaults.
class ThresholdConfig:
    DPD_THRESHOLD: float = 0.1       # Demographic Parity Difference > 0.1 -> Alert
    EOD_THRESHOLD: float = 0.08      # Equalized Odds Difference > 0.08 -> Alert
    ICD_THRESHOLD: float = 0.15      # Individual Counterfactual Disparity > 15% -> Intervention
    CAS_THRESHOLD: float = 0.20      # Causal Attribution Score > 0.20 -> Intervention

def get_tenant_thresholds(tenant_id: str) -> ThresholdConfig:
    # Placeholder for database retrieval
    return ThresholdConfig()
