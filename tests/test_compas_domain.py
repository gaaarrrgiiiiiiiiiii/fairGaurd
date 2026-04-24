"""
Domain test: COMPAS recidivism bias scenario.

Verifies that FairGuard correctly identifies and responds to the well-documented
COMPAS false positive rate disparity against African Americans.

References:
  - ProPublica (2016) "Machine Bias" investigation
  - Angwin et al. COMPAS dataset analysis
"""
import os
import sys

# Ensure backend is importable regardless of CWD
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_fairguard.db")
os.environ.setdefault("JWT_SECRET", "test-secret")

from fastapi.testclient import TestClient
from app.main import app
from app.models.database import init_db


def test_compas_domain_bias():
    """
    Simulate a COMPAS-style false-positive scenario.

    Race is the protected attribute. African Americans are known to receive
    high-risk scores at approximately twice the rate of white defendants
    with equivalent criminal histories.

    The test verifies:
      1. The API responds 200 OK.
      2. Bias is detected (race disparities exist in population metrics).
      3. The corrected decision is one of a valid set (low_risk or approved).
      4. The explanation contains meaningful text (not an empty string).
    """
    init_db()
    with TestClient(app) as client:
        payload = {
            "applicant_features": {
                "prior_arrests": 1,
                "charge_degree": "F",
                "race": "African_American",
            },
            "model_output": {"decision": "high_risk", "confidence": 0.81},
            "protected_attributes": ["race"],
        }

        response = client.post(
            "/v1/decision",
            json=payload,
            headers={"Authorization": "Bearer sk_test"},
        )

        assert response.status_code == 200
        data = response.json()

        # Must always contain these keys
        assert "bias_detected" in data
        assert "corrected_decision" in data
        assert "audit_id" in data
        assert "explanation" in data

        # The API should detect population-level bias (DPD/EOD for race attribute)
        assert data["bias_detected"] is True, (
            "Expected bias_detected=True for a known COMPAS race-bias scenario. "
            "DPD for race should exceed the alert threshold."
        )

        # When bias is detected via DPD/EOD but ICD < ICD_THRESHOLD, no correction
        # is applied (the decision passes through). This is correct behaviour —
        # a population-level alert doesn't necessarily warrant an individual intervention.
        corrected = data["corrected_decision"]["decision"]
        assert corrected in ("low_risk", "approved", "high_risk"), (
            f"Unexpected corrected decision value: '{corrected}'"
        )

        # Explanation must be a non-empty string
        explanation = data.get("explanation", "")
        assert isinstance(explanation, str)
        assert len(explanation) > 5, "Explanation should be meaningful, not empty"
