import requests
from typing import Dict, Any, List

class FairGuardClient:
    """
    FairGuard Python SDK
    Intercepts biased ML decisions in 5 lines of code.
    """
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        
    def evaluate(self, applicant_features: Dict[str, Any], model_output: Dict[str, Any], protected_attributes: List[str]):
        """
        Evaluate a single decision for bias and get a compliant correction if needed.
        """
        payload = {
            "applicant_features": applicant_features,
            "model_output": model_output,
            "protected_attributes": protected_attributes
        }
        
        # In a real SDK, we'd pass the key as an Authorization header
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.post(f"{self.base_url}/v1/decision", json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()

# Example Usage:
# Set FAIRGUARD_API_KEY in your environment before running:
#   export FAIRGUARD_API_KEY=sk_fgt_<your_key>
if __name__ == "__main__":
    import os
    _api_key = os.environ.get("FAIRGUARD_API_KEY", "")
    if not _api_key:
        raise RuntimeError("Set FAIRGUARD_API_KEY environment variable before running the SDK example.")
    client = FairGuardClient(api_key=_api_key)
    
    # 1. Your ML model makes a decision
    # decision = my_xgboost_model.predict(applicant)
    raw_decision = {"decision": "denied", "confidence": 0.73}
    applicant = {"age": 35, "income": 55000, "sex": "Female"}
    
    # 2. FairGuard evaluates and optionally corrects it
    result = client.evaluate(
        applicant_features=applicant,
        model_output=raw_decision,
        protected_attributes=["sex"]
    )
    
    print("Final Decision Issued:", result["corrected_decision"]["decision"])
    print("Compliance Explanation:", result["explanation"])
