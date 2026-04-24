"""Pydantic request/response schemas for the FairGuard API."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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
        description="List of attribute names to evaluate for bias.",
        examples=[["sex", "age"]],
    )


class DecisionResponse(BaseModel):
    original_decision: Dict[str, Any]
    corrected_decision: Dict[str, Any]
    bias_detected: bool
    explanation: Optional[str] = None
    audit_id: Optional[str] = None


class BiasScores(BaseModel):
    DPD: float = Field(..., description="Demographic Parity Difference")
    EOD: float = Field(..., description="Equalized Odds Difference")
    ICD: float = Field(..., description="Individual Counterfactual Disparity")
    CAS: float = Field(..., description="Causal Attribution Score")


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
