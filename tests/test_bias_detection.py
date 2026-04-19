import pytest
import os
import sys

# Add backend directory to sys.path to easily import routers/services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

def test_bias_detection_triggers_intervention():
    # As configured in our mocks, a Female target triggers the >15% ICD.
    payload = {
        "applicant_features": {"age": 35, "income": 55000, "education": "Bachelors", "sex": "Female"},
        "model_output": {"decision": "denied", "confidence": 0.73},
        "protected_attributes": ["sex"]
    }
    
    with TestClient(app) as client:
        response = client.post("/v1/decision", json=payload)
        assert response.status_code == 200
        data = response.json()
    
    assert data["bias_detected"] is True
    assert data["corrected_decision"]["decision"] == "approved"
    assert "bias correction operations" in data["explanation"]
    assert data["audit_id"] is not None

def test_fair_decision_passes_through():
    # As configured in our mocks, Male does not trigger the ICD > 15% threshold.
    payload = {
        "applicant_features": {"age": 35, "income": 55000, "education": "Bachelors", "sex": "Male"},
        "model_output": {"decision": "approved", "confidence": 0.89},
        "protected_attributes": ["sex"]
    }
    
    with TestClient(app) as client:
        response = client.post("/v1/decision", json=payload)
        assert response.status_code == 200
        data = response.json()
    
    assert data["bias_detected"] is False
    assert data["corrected_decision"]["decision"] == "approved"
    assert "No statistically significant bias detected." in data["explanation"]
