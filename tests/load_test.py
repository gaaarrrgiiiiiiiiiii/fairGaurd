from locust import HttpUser, task, between
import json

class FairGuardUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def evaluate_decision(self):
        payload = {
            "applicant_features": {"age": 28, "income": 45000, "sex": "Female"},
            "model_output": {"decision": "denied", "confidence": 0.65},
            "protected_attributes": ["sex"]
        }
        
        # Hit the evaluation endpoint
        self.client.post(
            "/v1/decision",
            json=payload,
            headers={"Authorization": "Bearer sk_test_123"},
            timeout=2.0
        )
