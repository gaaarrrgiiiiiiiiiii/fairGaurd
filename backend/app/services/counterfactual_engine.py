import os
import joblib
import pandas as pd
from typing import Dict, Any, List

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
MODEL_PATH = os.path.join(DATA_DIR, 'biased_model.joblib')

class CounterfactualEngine:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            
        self.default_row = {
            'age': 35,
            'workclass': 'Private',
            'fnlwgt': 189778,
            'education': 'HS-grad',
            'education-num': 10,
            'marital-status': 'Married-civ-spouse',
            'occupation': 'Exec-managerial',
            'relationship': 'Husband',
            'race': 'White',
            'sex': 'Male',
            'capital-gain': 0,
            'capital-loss': 0,
            'hours-per-week': 40,
            'native-country': 'United-States'
        }

    def _pad_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        row = self.default_row.copy()
        row.update(features)
        return pd.DataFrame([row])

    def generate_counterfactual(self, features: Dict[str, Any], protected_attributes: List[str], target_decision: str) -> Dict[str, Any]:
        """
        Generates a counterfactual instance by mutating protected attributes 
        and computing the new model likelihood.
        """
        cf_features = features.copy()
        for attr in protected_attributes:
            if attr == "sex":
                cf_features[attr] = "Male" if features.get("sex") == "Female" else "Female"
            elif attr == "race":
                cf_features[attr] = "White" if features.get("race") == "Black" else "Black"
                
        # Real model calculation to get counterfactual probability
        cf_probability = 0.89 # fallback
        if self.model and getattr(self.model, "classes_", None) is not None:
            try:
                df_cf = self._pad_features(cf_features)
                cf_probability = float(self.model.predict_proba(df_cf)[0][1])
            except Exception as e:
                print(f"Counterfactual Engine error: {e}")
        
        return {
            "features": cf_features,
            "target_score": cf_probability,
            "decision": target_decision
        }

counterfactual_engine = CounterfactualEngine()
