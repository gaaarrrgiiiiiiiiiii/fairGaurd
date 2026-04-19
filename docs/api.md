# FairGuard API Documentation

FairGuard exposes a sub-15ms REST API for routing ML decisions through our real-time bias interceptor.

## Authentication
Pass your client key using a Bearer token in the `Authorization` header.

## Endpoint: `POST /v1/decision`

Evaluate any ML output for statistical fairness bias prior to serving the decision to a human via your platform.

### Request Payload (JSON)
```json
{
  "applicant_features": {
    "age": 35,
    "income": 55000,
    "education": "Bachelors",
    "sex": "Female"
  },
  "model_output": {
    "decision": "denied",
    "confidence": 0.73
  },
  "protected_attributes": ["sex", "race"]
}
```

### Response Payload (JSON)
```json
{
  "original_decision": {
    "decision": "denied",
    "confidence": 0.73
  },
  "corrected_decision": {
    "decision": "approved",
    "confidence": 0.89,
    "correction_applied": true
  },
  "bias_detected": true,
  "explanation": "Application approved after bias correction operations on protected attributes ['sex']. Original probability was 73.0%, fair probability is 89.0%.",
  "audit_id": "8b3f2c5a-1b4e-4e9b-9c6d-5b3f2c5a1b4e"
}
```

## Endpoint: `GET /v1/report/generate`

Generates an EU AI Act compliant PDF tracking all decision interceptions.

**Headers needed:**
`Authorization: Bearer <API_KEY>`

**Response:**
Returns a raw `application/pdf` binary stream.
