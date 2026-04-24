"""
Unit tests for fairguard_sdk.py

Uses `responses` library to mock HTTP calls so tests run offline.
Install: pip install responses
"""
import os
import sys
import pytest

# Ensure sdk directory is importable
SDK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sdk"))
if SDK_DIR not in sys.path:
    sys.path.insert(0, SDK_DIR)

from fairguard_sdk import FairGuardClient

try:
    import responses as responses_lib
    HAS_RESPONSES = True
except ImportError:
    responses_lib = None
    HAS_RESPONSES = False


# ---------------------------------------------------------------------------
# Client initialisation
# ---------------------------------------------------------------------------

class TestClientInit:
    def test_default_base_url(self):
        client = FairGuardClient(api_key="sk_test")
        assert "localhost" in client.base_url or "8000" in client.base_url

    def test_custom_base_url(self):
        client = FairGuardClient(api_key="sk_test", base_url="https://api.fairguard.ai")
        assert client.base_url == "https://api.fairguard.ai"

    def test_api_key_stored(self):
        client = FairGuardClient(api_key="sk_test_123")
        assert client.api_key == "sk_test_123"


# ---------------------------------------------------------------------------
# Mocked HTTP tests — skipped unless `responses` is installed
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_RESPONSES, reason="pip install responses")
def test_evaluate_success():
    with responses_lib.RequestsMock() as rsps:
        rsps.add(
            rsps.POST,
            "http://localhost:8000/v1/decision",
            json={
                "original_decision":  {"decision": "denied",  "confidence": 0.73},
                "corrected_decision": {"decision": "approved", "confidence": 0.89},
                "bias_detected": True,
                "explanation": "Bias corrected due to sex disparity.",
                "audit_id": "abc12345-0000-0000-0000-000000000000",
            },
            status=200,
        )
        client = FairGuardClient(api_key="sk_test")
        result = client.evaluate(
            features={"age": 35, "income": 55000, "sex": "Female"},
            model_output={"decision": "denied", "confidence": 0.73},
            protected_attributes=["sex"],
        )
        assert result["bias_detected"] is True
        assert result["corrected_decision"]["decision"] == "approved"
        assert "audit_id" in result


@pytest.mark.skipif(not HAS_RESPONSES, reason="pip install responses")
def test_evaluate_raises_on_error():
    with responses_lib.RequestsMock() as rsps:
        rsps.add(
            rsps.POST,
            "http://localhost:8000/v1/decision",
            json={"detail": "Rate limit exceeded"},
            status=429,
        )
        client = FairGuardClient(api_key="sk_test")
        with pytest.raises(Exception):
            client.evaluate(
                features={"age": 30},
                model_output={"decision": "denied", "confidence": 0.5},
                protected_attributes=["sex"],
            )


@pytest.mark.skipif(not HAS_RESPONSES, reason="pip install responses")
def test_check_drift_mocked():
    with responses_lib.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "http://localhost:8000/v1/drift/status",
            json={
                "drift_detected": False,
                "ks_statistic": 0.041,
                "p_value": 0.23,
                "message": "Model output distribution is stable.",
            },
            status=200,
        )
        client = FairGuardClient(api_key="sk_test")
        result = client.check_drift()
        assert result["drift_detected"] is False
        assert result["ks_statistic"] == 0.041
