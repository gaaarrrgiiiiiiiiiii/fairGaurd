<div align="center">

# 🛡️ FairGuard

### The Real-Time AI Fairness Firewall

[![CI](https://github.com/your-org/fairguard/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/fairguard/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![EU AI Act](https://img.shields.io/badge/EU_AI_Act-Article_13-003399?style=flat-square)](https://artificialintelligenceact.eu)

**Intercept biased ML decisions in real time — before they affect a single user.**

[Quick Start](#-quick-start) · [How It Works](#-how-it-works) · [API Reference](#-api-reference) · [SDK](#-sdk) · [Contributing](#-contributing)

</div>

---

## What Is FairGuard?

FairGuard is a **middleware layer** that sits between your ML model and your users. Every decision passes through a 4-stage fairness pipeline that:

1. Detects demographic bias using statistical metrics (DPD, EOD, ICD, CAS)
2. Proves causality using DoWhy causal graphs
3. Generates counterfactual corrections via DiCE-ML
4. Produces EU AI Act Article 13 compliance reports

**Hot-path latency: <50 ms.** LLM explanation generation is fully async (fire-and-forget).

---

## Architecture

```
Your ML Model → FairGuard Middleware → End User
                 │
                 ├─ [1] BiasDetector   (DPD / EOD / ICD / CAS)
                 ├─ [2] CausalEngine   (DoWhy — proves causality)
                 ├─ [3] Corrector      (DiCE-ML counterfactual)
                 └─ [4] LLMService     (EU AI Act explanation, async)
                          │
                     AuditLog DB ──→ SSE Stream ──→ Dashboard
```

**Key design choices:**

| Choice | Rationale |
|--------|-----------|
| FastAPI + async | Sub-50ms decision endpoint |
| SSE over WebSocket | Simpler, proxy-friendly real-time push |
| Fire-and-forget LLM | LLM off the hot path; explanation arrives async |
| SQLite default | Zero-config dev; `DATABASE_URL` → PostgreSQL for prod |
| In-process pub/sub | Single-worker; upgrade path: Redis Pub/Sub |

---

## Features

- ⚡ **<50ms decision latency** — bias + causal run in parallel thread-pool executors
- 🔍 **4 bias metrics** — DPD, EOD, ICD (individual counterfactual), CAS (causal attribution)
- 🧮 **DiCE-ML counterfactuals** — 3-tier fallback (DiCE → attribute-flip → neutral)
- 📡 **Real-time SSE stream** — live decision feed to the dashboard, no polling
- 📄 **PDF compliance reports** — EU AI Act Article 13 format, one click
- 🔐 **JWT auth** — per-tenant API keys, Bearer tokens
- 🐳 **Docker-ready** — multi-stage build, non-root user, health checks
- 🧪 **Test suite** — pytest integration tests with coverage

---

## Quick Start

### Option A — Docker Compose (recommended)

```bash
git clone https://github.com/your-org/fairguard.git
cd fairguard

# Copy and configure environment variables
cp .env.example .env
# Edit .env: set JWT_SECRET, FAIRGUARD_API_KEYS, optionally GEMINI_API_KEY

# Start everything
docker compose up --build
```

- Dashboard: http://localhost:3000
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Option B — Local Development

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env      # then edit .env
# Prepare ML model + dataset
cd .. && python data/prep_adult_data.py
# Start API
cd backend && uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd frontend
cp .env.example .env            # set VITE_API_TOKEN if needed
npm install
npm run dev                     # http://localhost:5173
```

---

## Environment Variables

Copy `.env.example` → `.env`. **Never commit `.env`.**

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET` | ✅ prod | 32+ char random secret (`secrets.token_hex(32)`) |
| `FAIRGUARD_API_KEYS` | ✅ prod | JSON: `{"sk_fgt_xxx": "tenant_name"}` |
| `FAIRGUARD_DEV_MODE` | dev only | `true` skips auth — **never in prod** |
| `DATABASE_URL` | optional | SQLite (default) or `postgresql://...` |
| `GEMINI_API_KEY` | optional | LLM for explanations (Gemini) |
| `GROQ_API_KEY` | optional | LLM fallback (Llama) |
| `MISTRAL_API_KEY` | optional | LLM fallback (Mistral) |
| `VITE_API_BASE_URL` | frontend | Backend URL (`http://localhost:8000`) |
| `VITE_API_TOKEN` | frontend | JWT for dashboard auth (empty if DEV_MODE) |

Generate secrets:
```bash
# JWT secret
python -c "import secrets; print(secrets.token_hex(32))"

# API key
python -c "import secrets; print('sk_fgt_' + secrets.token_hex(16))"
```

---

## API Reference

### Authentication

All protected endpoints require `Authorization: Bearer <jwt>`.

Get a JWT:
```bash
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "my_tenant", "api_key": "sk_fgt_..."}'
```

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | ❌ | Liveness probe |
| `POST` | `/v1/auth/token` | ❌ | Exchange API key → JWT |
| `POST` | `/v1/decision` | ✅ | Evaluate decision for bias |
| `GET` | `/v1/drift/status` | ✅ | Model drift detection |
| `GET` | `/v1/report/generate` | ✅ | Download PDF compliance report |
| `GET` | `/v1/stream/decisions` | ✅ | SSE — live decision feed |
| `GET` | `/v1/stream/analytics` | ✅ | Real-time aggregate stats |

### POST `/v1/decision` — Example

```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_features": {"age": 35, "income": 55000, "sex": "Female"},
    "model_output": {"decision": "denied", "confidence": 0.73},
    "protected_attributes": ["sex"]
  }'
```

**Response:**
```json
{
  "original_decision": {"decision": "denied", "confidence": 0.73},
  "corrected_decision": {"decision": "approved", "confidence": 0.68, "correction_applied": true},
  "bias_detected": true,
  "explanation": "Bias correction applied: 'denied' → 'approved' (confidence 68%, method=attribute-flip) on ['sex']. Full EU AI Act Article 13 rationale generating asynchronously.",
  "audit_id": "a1b2c3d4-..."
}
```

### GET `/v1/stream/decisions` — SSE

```javascript
const es = new EventSource('http://localhost:8000/v1/stream/decisions?token=<jwt>');
es.addEventListener('decision', (e) => {
  const event = JSON.parse(e.data);
  console.log(event.audit_id, event.bias_detected);
});
```

---

## SDK

```python
pip install requests  # SDK uses stdlib only
```

```python
import os
from sdk.fairguard_sdk import FairGuardClient

client = FairGuardClient(api_key=os.environ["FAIRGUARD_API_KEY"])

result = client.evaluate(
    applicant_features={"age": 35, "income": 55000, "sex": "Female"},
    model_output={"decision": "denied", "confidence": 0.73},
    protected_attributes=["sex"],
)

print(result["corrected_decision"]["decision"])  # "approved"
print(result["bias_detected"])                   # True
```

---

## Testing

```bash
# Run full test suite
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=backend/app --cov-report=term-missing

# Single test class
pytest tests/test_pipeline_integration.py::TestDecisionEndpoint -v
```

CI runs on every push/PR via GitHub Actions (`.github/workflows/ci.yml`).

---

## Project Structure

```
fairguard/
├── backend/
│   ├── app/
│   │   ├── auth/           # JWT handling
│   │   ├── models/         # SQLAlchemy ORM, audit log, analytics
│   │   ├── routers/        # FastAPI routes (decisions, drift, report, stream, auth)
│   │   └── services/       # Core ML engines
│   ├── Dockerfile          # Multi-stage production image
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/     # React UI
│       ├── hooks/          # useSSE, useAnalytics
│       └── services/       # API client
├── data/                   # ML model + dataset scripts
├── sdk/                    # Python SDK
├── tests/                  # pytest integration tests
├── .github/workflows/      # CI/CD (GitHub Actions)
├── docker-compose.yml
└── .env.example            # ← copy this to .env
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, conventions, and PR process.

**Quick contribution flow:**
1. Fork → branch (`feat/your-feature`)
2. Code + tests
3. `pytest tests/ -v` must pass
4. Open PR targeting `main`

---

## License

[MIT](LICENSE) — © FairGuard Contributors
