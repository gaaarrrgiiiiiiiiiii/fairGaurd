"""
CorrectorEngine — applies bias corrections.

C3 (fire-and-forget):
  apply_correction_fast() → returns decision + template explanation synchronously.
  No LLM call on the hot path. Caller schedules generate_explanation_async()
  as a FastAPI BackgroundTask so the HTTP response is returned immediately.
"""
import logging
from typing import Any, Dict, List, Tuple

from app.services.counterfactual_engine import counterfactual_engine

logger = logging.getLogger(__name__)

_DECISION_FLIP = {
    "denied":    "approved",
    "high_risk": "low_risk",
}


class CorrectorEngine:

    # ------------------------------------------------------------------
    # Hot-path — synchronous, no I/O
    # ------------------------------------------------------------------
    def apply_correction_fast(
        self,
        features: Dict[str, Any],
        model_output: Dict[str, Any],
        protected_attributes: List[str],
        bias_scores: dict,
    ) -> Tuple[Dict[str, Any], str]:
        """
        C3: Returns corrected decision + deterministic placeholder in <1 ms.
        LLM explanation is generated separately via generate_explanation_async().
        """
        original = model_output.get("decision", "denied")
        target   = _DECISION_FLIP.get(original, original)

        cf = counterfactual_engine.generate_counterfactual(
            features, protected_attributes, target
        )

        corrected_decision = {
            "decision":           cf["decision"],
            "confidence":         cf["target_score"],
            "correction_applied": True,
            "cf_method":          cf.get("method", "unknown"),
        }

        # Template explanation — human-readable while LLM generates async
        placeholder = (
            f"Bias correction applied: '{original}' → '{cf['decision']}' "
            f"(confidence {cf['target_score']:.0%}, method={cf.get('method','?')}) "
            f"on protected attributes {protected_attributes}. "
            f"Full EU AI Act Article 13 rationale is generating asynchronously."
        )

        return corrected_decision, placeholder

    # ------------------------------------------------------------------
    # Background task — async, called after response is sent
    # ------------------------------------------------------------------
    async def generate_explanation_async(
        self,
        features: Dict[str, Any],
        original_decision: str,
        corrected_decision: str,
        protected_attributes: List[str],
    ) -> str:
        """C2+C3: Non-blocking LLM call — run as BackgroundTask."""
        from app.services.llm_service import llm_service  # late import avoids cycles

        try:
            return await llm_service.generate_explanation(
                features=features,
                original_decision=original_decision,
                corrected_decision=corrected_decision,
                protected_attributes=protected_attributes,
            )
        except Exception as exc:
            logger.warning("Background explanation failed: %s", exc)
            return (
                f"Decision overridden '{original_decision}' → '{corrected_decision}' "
                f"on {protected_attributes} per EU AI Act Article 13."
            )


corrector = CorrectorEngine()
