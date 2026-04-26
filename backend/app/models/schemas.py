"""
Pydantic request/response schemas for the FairGuard API.

H4 — All inputs are strictly validated:
  • applicant_features: bounded numeric fields, whitelisted string enums
  • model_output: decision enum + confidence [0,1]
  • protected_attributes: whitelist of known attrs, max 5
"""
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re

# ---------------------------------------------------------------------------
# Allowed values
# ---------------------------------------------------------------------------
_ALLOWED_DECISIONS  = {"approved", "denied", "high_risk", "low_risk", "pending"}
_ALLOWED_ATTRIBUTES = {"sex", "race", "age", "income", "nationality", "religion"}
_ALLOWED_SEX_VALUES = {"Male", "Female", "Non-binary", "Other"}
_ALLOWED_RACE_VALUES = {
    "White", "Black", "Asian", "Hispanic",
    "American-Indian-Eskimo", "Other", "Unknown",
}
_SAFE_STRING_RE = re.compile(r"^[\w\s\-\.]+$")  # no SQL/injection chars


def _safe_string(v: str, field: str) -> str:
    """Reject strings containing special characters."""
    if not _SAFE_STRING_RE.match(str(v)):
        raise ValueError(
            f"'{field}' contains invalid characters. "
            "Only alphanumeric, spaces, hyphens, and dots are allowed."
        )
    return v


# ---------------------------------------------------------------------------
# DecisionRequest
# ---------------------------------------------------------------------------
class DecisionRequest(BaseModel):
    applicant_features: Dict[str, Any] = Field(
        ...,
        description="Feature vector for the individual being evaluated.",
        examples=[{"age": 35, "income": 55000, "sex": "Female"}],
    )
    model_output: Dict[str, Any] = Field(
        ...,
        description="Raw output from the upstream ML model.",
        examples=[{"decision": "denied", "confidence": 0.73}],
    )
    protected_attributes: Optional[List[str]] = Field(
        default=None,
        description="Attribute names to evaluate for bias (max 5).",
        examples=[["sex", "age"]],
    )

    # ── model_output validation ──────────────────────────────────────────
    @field_validator("model_output")
    @classmethod
    def validate_model_output(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if "decision" not in v:
            raise ValueError("model_output must contain a 'decision' field.")
        decision = str(v["decision"]).lower()
        if decision not in _ALLOWED_DECISIONS:
            raise ValueError(
                f"model_output.decision '{decision}' is not allowed. "
                f"Must be one of: {sorted(_ALLOWED_DECISIONS)}"
            )
        v["decision"] = decision  # normalise to lowercase

        if "confidence" in v:
            try:
                conf = float(v["confidence"])
            except (TypeError, ValueError):
                raise ValueError("model_output.confidence must be a number.")
            if not (0.0 <= conf <= 1.0):
                raise ValueError(
                    f"model_output.confidence must be between 0 and 1, got {conf}."
                )
            v["confidence"] = round(conf, 6)

        return v

    # ── protected_attributes validation ─────────────────────────────────
    @field_validator("protected_attributes")
    @classmethod
    def validate_protected_attributes(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        if len(v) > 5:
            raise ValueError("protected_attributes may contain at most 5 items.")
        normalised = []
        for attr in v:
            a = str(attr).lower().strip()
            if a not in _ALLOWED_ATTRIBUTES:
                raise ValueError(
                    f"Protected attribute '{a}' is not supported. "
                    f"Allowed: {sorted(_ALLOWED_ATTRIBUTES)}"
                )
            normalised.append(a)
        return normalised

    # ── applicant_features validation ────────────────────────────────────
    @field_validator("applicant_features")
    @classmethod
    def validate_applicant_features(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError("applicant_features must not be empty.")
        if len(v) > 30:
            raise ValueError("applicant_features may not have more than 30 fields.")

        # Per-field validation
        if "age" in v:
            try:
                age = float(v["age"])
            except (TypeError, ValueError):
                raise ValueError("'age' must be a number.")
            if not (0 <= age <= 120):
                raise ValueError(f"'age' must be between 0 and 120, got {age}.")
            v["age"] = int(age)

        if "income" in v:
            try:
                income = float(v["income"])
            except (TypeError, ValueError):
                raise ValueError("'income' must be a number.")
            if not (0 <= income <= 10_000_000):
                raise ValueError(
                    f"'income' must be between 0 and 10,000,000, got {income}."
                )
            v["income"] = round(income, 2)

        if "sex" in v:
            sex_val = str(v["sex"]).strip()
            # Accept case-insensitive, normalise to title-case
            matched = next(
                (s for s in _ALLOWED_SEX_VALUES if s.lower() == sex_val.lower()), None
            )
            if matched is None:
                raise ValueError(
                    f"'sex' value '{sex_val}' is not recognised. "
                    f"Allowed: {sorted(_ALLOWED_SEX_VALUES)}"
                )
            v["sex"] = matched

        if "race" in v:
            race_val = str(v["race"]).strip()
            matched = next(
                (r for r in _ALLOWED_RACE_VALUES if r.lower() == race_val.lower()), None
            )
            if matched is None:
                raise ValueError(
                    f"'race' value '{race_val}' is not recognised. "
                    f"Allowed: {sorted(_ALLOWED_RACE_VALUES)}"
                )
            v["race"] = matched

        # Reject string values with special characters (injection guard)
        for key, val in v.items():
            if isinstance(val, str):
                _safe_string(val, key)

        return v


# ---------------------------------------------------------------------------
# DecisionResponse
# ---------------------------------------------------------------------------
class DecisionResponse(BaseModel):
    original_decision: Dict[str, Any]
    corrected_decision: Dict[str, Any]
    bias_detected: bool
    explanation: Optional[str] = None
    audit_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
class BiasScores(BaseModel):
    DPD: float = Field(..., description="Demographic Parity Difference")
    EOD: float = Field(..., description="Equalized Odds Difference")
    ICD: float = Field(..., description="Individual Counterfactual Disparity")
    CAS: float = Field(..., description="Causal Attribution Score")


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
