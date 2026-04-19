from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class DecisionRequest(BaseModel):
    applicant_features: Dict[str, Any]
    model_output: Dict[str, Any]
    protected_attributes: Optional[List[str]] = None

class DecisionResponse(BaseModel):
    original_decision: Dict[str, Any]
    corrected_decision: Dict[str, Any]
    bias_detected: bool
    explanation: Optional[str] = None
    audit_id: Optional[str] = None
