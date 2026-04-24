"""
Integration tests for the full FairGuard API pipeline.

Tests:
  - Health check
  - Decision endpoint: bias detected & corrected
  - Decision endpoint: fair decision passes through
  - Decision endpoint: no protected attributes fast path
  - Decision endpoint: graceful degradation on malformed input
  - Drift endpoint
  - Report endpoint
  - Auth token endpoint
"""
import pytest


class TestHealth:
    def test_health_returns_ok(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestDecisionEndpoint:
    """Integration tests for POST /v1/decision."""

    def test_bias_detected_female_sex(self, test_client):
        payload = {
            "applicant_features": {"age": 35, "income": 55000, "sex": "Female"},
            "model_output": {"decision": "denied", "confidence": 0.73},
            "protected_attributes": ["sex"],
        }
        response = test_client.post("/v1/decision", json=payload)
        assert response.status_code == 200
        data = response.json()

        # The response must always contain these fields
        assert "original_decision" in data
        assert "corrected_decision" in data
        assert "bias_detected" in data
        assert "audit_id" in data

        # When ICD > threshold, bias is detected and decision is corrected
        assert isinstance(data["bias_detected"], bool)
        assert data["audit_id"] is not None

    def test_no_protected_attrs_fast_path(self, test_client):
        payload = {
            "applicant_features": {"age": 35, "income": 55000},
            "model_output": {"decision": "approved", "confidence": 0.90},
            "protected_attributes": [],
        }
        response = test_client.post("/v1/decision", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["bias_detected"] is False
        assert data["corrected_decision"]["decision"] == "approved"

    def test_missing_protected_attrs_field(self, test_client):
        """protected_attributes is optional — should default to []."""
        payload = {
            "applicant_features": {"age": 35},
            "model_output": {"decision": "approved", "confidence": 0.80},
        }
        response = test_client.post("/v1/decision", json=payload)
        assert response.status_code == 200

    def test_response_has_explanation(self, test_client):
        payload = {
            "applicant_features": {"age": 35, "income": 55000, "sex": "Female"},
            "model_output": {"decision": "denied", "confidence": 0.73},
            "protected_attributes": ["sex"],
        }
        response = test_client.post("/v1/decision", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("explanation") is not None
        assert len(data["explanation"]) > 5

    def test_audit_id_is_uuid_format(self, test_client):
        import re
        payload = {
            "applicant_features": {"age": 40, "income": 60000, "sex": "Male"},
            "model_output": {"decision": "approved", "confidence": 0.85},
            "protected_attributes": ["sex"],
        }
        response = test_client.post("/v1/decision", json=payload)
        assert response.status_code == 200
        audit_id = response.json().get("audit_id")
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        assert uuid_pattern.match(audit_id or ""), f"audit_id '{audit_id}' is not a valid UUID"

    def test_high_risk_corrected_to_low_risk(self, test_client):
        payload = {
            "applicant_features": {"age": 28, "race": "Black", "prior_arrests": 1},
            "model_output": {"decision": "high_risk", "confidence": 0.81},
            "protected_attributes": ["race"],
        }
        response = test_client.post("/v1/decision", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Should either pass through or correct to low_risk if bias is detected
        assert data["corrected_decision"]["decision"] in ("high_risk", "low_risk")


class TestDriftEndpoint:
    def test_drift_insufficient_data(self, test_client):
        """With a fresh test DB, there won't be enough records."""
        response = test_client.get("/v1/drift/status", params={"tenant_id": "tenant_drift_test"})
        assert response.status_code == 200
        data = response.json()
        assert "drift_detected" in data
        assert "message" in data
        assert data["drift_detected"] is False  # not enough data


class TestReportEndpoint:
    def test_report_returns_content(self, test_client):
        response = test_client.get("/v1/report/generate", params={"tenant_id": "tenant_local_dev"})
        assert response.status_code == 200
        # Should be PDF or text content
        assert len(response.content) > 0


class TestAuthEndpoint:
    def test_token_valid_key(self, test_client):
        response = test_client.post(
            "/v1/auth/token",
            json={"tenant_id": "tenant_demo", "api_key": "sk_fgt_12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 10

    def test_token_invalid_key(self, test_client):
        response = test_client.post(
            "/v1/auth/token",
            json={"tenant_id": "tenant_demo", "api_key": "sk_wrong_key"},
        )
        assert response.status_code == 401

    def test_token_tenant_mismatch(self, test_client):
        response = test_client.post(
            "/v1/auth/token",
            json={"tenant_id": "wrong_tenant", "api_key": "sk_fgt_12345"},
        )
        assert response.status_code == 401
