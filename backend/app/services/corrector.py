from typing import Dict, Any, Tuple
from app.services.counterfactual_engine import counterfactual_engine

class CorrectorEngine:
    def __init__(self):
        pass
        
    def apply_correction(
        self, 
        features: Dict[str, Any], 
        model_output: Dict[str, Any], 
        protected_attributes: list, 
        bias_scores: dict
    ) -> Tuple[Dict[str, Any], str]:
        
        if model_output.get("decision") == "denied":
            target = "approved"
        elif model_output.get("decision") == "high_risk":
            target = "low_risk"
        else:
            target = "denied"
        
        cf = counterfactual_engine.generate_counterfactual(features, protected_attributes, target)
        
        orig_prob = model_output.get("confidence", 0.0)
        new_prob = cf["target_score"]
        
        from app.services.llm_service import llm_service
        
        corrected_decision = {
            "decision": cf["decision"],
            "confidence": new_prob,
            "correction_applied": True
        }
        
        explanation = llm_service.generate_explanation(
            features=features,
            original_decision=model_output.get("decision", "unknown"),
            corrected_decision=cf["decision"],
            protected_attributes=protected_attributes
        )
        
        return corrected_decision, explanation

corrector = CorrectorEngine()
