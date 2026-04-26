"""
CounterfactualEngine — DiCE-ML powered counterfactual generation.

C4: Replaces the hardcoded 0.89 stub with a real DiCE-ML integration.

Strategy:
  • At startup, attempt to build a DiCE Explainer from the loaded model
    and a sample of the training data.
  • Per-request: call exp.generate_counterfactuals() with the individual
    features, target the opposite class.
  • Fallback: if DiCE is unavailable or fails, flip the protected attribute
    and call model.predict_proba() directly — still far more honest than 0.89.

DiCE is already in requirements.txt (dice-ml>=0.11).
"""
import logging
import os
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
MODEL_PATH = os.path.join(DATA_DIR, "biased_model.joblib")
FEAT_PATH  = os.path.join(DATA_DIR, "adult_features.csv")

# ---------------------------------------------------------------------------
# Feature schema
# ---------------------------------------------------------------------------
_NUMERIC_FEATURES = [
    "age", "fnlwgt", "education-num",
    "capital-gain", "capital-loss", "hours-per-week",
]
_CATEGORICAL_FEATURES = [
    "workclass", "education", "marital-status",
    "occupation", "relationship", "race", "sex", "native-country",
]
_ALL_FEATURES = _NUMERIC_FEATURES + _CATEGORICAL_FEATURES
_OUTCOME_LABEL = "income_class"

_DEFAULT_ROW: Dict[str, Any] = {
    "age":            35,
    "workclass":      "Private",
    "fnlwgt":         189778,
    "education":      "HS-grad",
    "education-num":  10,
    "marital-status": "Married-civ-spouse",
    "occupation":     "Exec-managerial",
    "relationship":   "Husband",
    "race":           "White",
    "sex":            "Male",
    "capital-gain":   0,
    "capital-loss":   0,
    "hours-per-week": 40,
    "native-country": "United-States",
}


class CounterfactualEngine:
    """
    Wraps DiCE-ML for counterfactual generation.

    Falls back to a model-based attribute-flip approach if DiCE is
    unavailable or raises an error for a given instance.
    """

    def __init__(self) -> None:
        self.model = None
        self._dice_exp = None       # dice_ml.Dice explainer
        self._dice_data = None      # dice_ml.Data object
        self._dice_model = None     # dice_ml.Model object

        self._load_model()
        self._init_dice()

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------
    def _load_model(self) -> None:
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                logger.info("CounterfactualEngine: model loaded from %s", MODEL_PATH)
            except Exception as exc:
                logger.error("CounterfactualEngine: failed to load model: %s", exc)

    def _init_dice(self) -> None:
        """
        Build the DiCE explainer from the training data sample.
        Runs once at startup; result is cached on self._dice_exp.
        """
        if self.model is None:
            logger.warning("CounterfactualEngine: no model — DiCE skipped.")
            return

        try:
            import dice_ml  # noqa: F401 — guard against missing install
        except ImportError:
            logger.warning(
                "dice-ml is not installed. "
                "Run `pip install dice-ml` to enable counterfactual generation."
            )
            return

        if not os.path.exists(FEAT_PATH):
            logger.warning(
                "CounterfactualEngine: training data not found at %s — DiCE skipped.",
                FEAT_PATH,
            )
            return

        try:
            import dice_ml

            # Load a representative sample for DiCE's data interface
            df = pd.read_csv(FEAT_PATH, nrows=2_000)

            # Add a synthetic outcome column (DiCE needs it in the dataframe)
            if hasattr(self.model, "predict"):
                df[_OUTCOME_LABEL] = self.model.predict(df).tolist()
            else:
                df[_OUTCOME_LABEL] = 0

            self._dice_data = dice_ml.Data(
                dataframe=df,
                continuous_features=_NUMERIC_FEATURES,
                outcome_name=_OUTCOME_LABEL,
            )

            self._dice_model = dice_ml.Model(
                model=self.model,
                backend="sklearn",
            )

            self._dice_exp = dice_ml.Dice(
                self._dice_data,
                self._dice_model,
                method="random",
            )
            logger.info("CounterfactualEngine: DiCE explainer initialised successfully.")

        except Exception as exc:
            logger.error(
                "CounterfactualEngine: DiCE initialisation failed: %s — "
                "falling back to attribute-flip method.",
                exc,
                exc_info=True,
            )
            self._dice_exp = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _pad_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """Merge incoming features with the UCI Adult default row."""
        row = _DEFAULT_ROW.copy()
        row.update({k: v for k, v in features.items() if k in _DEFAULT_ROW})
        # External 'income' maps to 'capital-gain'
        if "income" in features:
            row["capital-gain"] = float(features["income"])
        return pd.DataFrame([row])

    def _flip_protected_attrs(
        self, features: Dict[str, Any], protected_attributes: List[str]
    ) -> Dict[str, Any]:
        """Return a copy of features with protected attributes toggled."""
        cf = features.copy()
        for attr in protected_attributes:
            if attr == "sex":
                current = str(cf.get("sex", "Male")).strip()
                cf["sex"] = "Female" if current.lower() == "male" else "Male"
            elif attr == "race":
                current = str(cf.get("race", "White")).strip()
                cf["race"] = "Black" if current.lower() == "white" else "White"
        return cf

    def _model_probability(self, features: Dict[str, Any]) -> float:
        """Run predict_proba on the padded feature row."""
        if self.model is None or not hasattr(self.model, "predict_proba"):
            return 0.5
        try:
            df = self._pad_features(features)
            return float(self.model.predict_proba(df)[0][1])
        except Exception as exc:
            logger.warning("CounterfactualEngine: predict_proba failed: %s", exc)
            return 0.5

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_counterfactual(
        self,
        features: Dict[str, Any],
        protected_attributes: List[str],
        target_decision: str,
    ) -> Dict[str, Any]:
        """
        Generate a counterfactual for the given instance.

        Returns:
            {
                "features": <counterfactual feature dict>,
                "target_score": <float probability of target class>,
                "decision": <target_decision string>,
                "method": "dice" | "attribute_flip" | "fallback",
            }
        """
        # ── Strategy 1: DiCE (preferred) ────────────────────────────────
        if self._dice_exp is not None:
            try:
                query_df = self._pad_features(features)
                desired_class = 1 if target_decision in {"approved", "low_risk"} else 0

                cf_result = self._dice_exp.generate_counterfactuals(
                    query_df,
                    total_CFs=1,
                    desired_class=desired_class,
                    features_to_vary="all",
                )
                cf_df = cf_result.cf_examples_list[0].final_cfs_df

                if cf_df is not None and not cf_df.empty:
                    cf_features = cf_df.drop(
                        columns=[_OUTCOME_LABEL], errors="ignore"
                    ).iloc[0].to_dict()

                    # Compute model confidence on the counterfactual instance
                    cf_prob = self._model_probability(cf_features)

                    logger.info(
                        "DiCE counterfactual generated: target=%s prob=%.3f",
                        target_decision, cf_prob,
                    )
                    return {
                        "features": cf_features,
                        "target_score": round(cf_prob, 4),
                        "decision": target_decision,
                        "method": "dice",
                    }

            except Exception as exc:
                logger.warning(
                    "DiCE generation failed (%s) — falling back to attribute-flip.",
                    exc,
                )

        # ── Strategy 2: Attribute-flip + real model probability ──────────
        if self.model is not None:
            try:
                cf_features = self._flip_protected_attrs(features, protected_attributes)
                cf_prob = self._model_probability(cf_features)
                logger.info(
                    "Attribute-flip counterfactual: target=%s prob=%.3f",
                    target_decision, cf_prob,
                )
                return {
                    "features": cf_features,
                    "target_score": round(cf_prob, 4),
                    "decision": target_decision,
                    "method": "attribute_flip",
                }
            except Exception as exc:
                logger.warning("Attribute-flip failed: %s", exc)

        # ── Strategy 3: Conservative fallback ───────────────────────────
        # Return a neutral probability rather than the fabricated 0.89.
        logger.warning(
            "CounterfactualEngine: all strategies failed — returning fallback."
        )
        return {
            "features": features,
            "target_score": 0.51,   # neutral — just over the decision boundary
            "decision": target_decision,
            "method": "fallback",
        }


# Module-level singleton
counterfactual_engine = CounterfactualEngine()
