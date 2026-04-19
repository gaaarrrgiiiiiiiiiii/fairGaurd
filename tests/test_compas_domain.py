from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_compas_domain_bias():
    """
    Simulating a failure domain from COMPAS criminal recidivism data.
    Race is the protected attribute.
    """
    with TestClient(app) as client:
        # A scenario where COMPAS is known to exhibit false positives for African Americans
        payload = {
            "applicant_features": {"prior_arrests": 1, "charge_degree": "F", "race": "African_American"},
            "model_output": {"decision": "high_risk", "confidence": 0.81},
            "protected_attributes": ["race"]
        }
        
        response = client.post(
            "/v1/decision",
            json=payload,
            headers={"Authorization": "Bearer sk_test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # In our mock logic, African_American is flagged for bias exactly like Female was.
        assert data["bias_detected"] == True
        assert data["corrected_decision"]["decision"] == "low_risk"
        assert "population metrics" in data["explanation"] or "bias correction" in data["explanation"]
