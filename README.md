<div align="center">

<img src="docs/assets/logo.svg" alt="FairGuard Logo" width="120" />

# FairGuard

### Real-Time AI Fairness Firewall

**Intercept biased ML decisions before they reach users — in production, at scale.**

[![CI](https://github.com/your-org/fairguard/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/fairguard/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Art.%2010%2F12%2F13%2F14-blue)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[**Live Demo**](https://fairguard-frontend-207958058488.us-central1.run.app) · [**API Docs**](https://fairguard-api-207958058488.us-central1.run.app/docs) · [**Report a Bug**](https://github.com/gaaarrrgiiiiiiiiiii/fairGaurd/issues) · [**Request Feature**](https://github.com/gaaarrrgiiiiiiiiiii/fairGaurd/issues)

</div>

---

## 🔍 What is FairGuard?

Most fairness tools run *offline* — they analyze historical data after harm is already done. **FairGuard is different.** It sits inline with your inference pipeline and intercepts biased decisions in real time, before they affect a user.

```
Your ML Model → FairGuard Firewall → User
                     ↑
           Bias detected? Correct it.
           Audit log written.
           Webhook fired.
           Compliance updated.
```

FairGuard works across three high-stakes domains out of the box:

| Domain | Decisions | Protected Attributes |
|---|---|---|
| 🏦 **Lending** | `approved / denied` | sex, race, age |
| 🏥 **Healthcare** | `treatment_recommended / referral_only` | race, sex, age, disability |
| ⚖️ **Criminal Justice** | `low_risk / medium_risk / high_risk` | race, sex, age |

---

## ✨ Features

| Category | Capability |
|---|---|
| **Bias Detection** | Statistical parity (DPD), equalized odds (EOD), individual counterfactual disparity (ICD), composite alignment score (CAS) |
| **Causal Inference** | DoWhy-powered DAG analysis with per-domain causal paths and ACE scoring |
| **Real-time Correction** | DiCE counterfactual generation with detect-only or detect-and-correct modes |
| **RBAC** | JWT-based roles: `admin`, `auditor`, `viewer` with route-level enforcement |
| **Immutable Audit Log** | SHA-256 hash-chain across all decisions — tamper-evident by design |
| **Compliance Reports** | EU AI Act Art. 10/12/13/14 PDF reports with domain breakdown and chain verification |
| **Multi-Domain** | Plug-in domain registry: lending, healthcare, criminal justice (extendable) |
| **Webhooks** | HMAC-signed event webhooks for `bias.detected` and `drift.detected` |
| **Real-time SSE** | Live decision stream; Redis Pub/Sub backend for multi-worker deployments |
| **Batch API** | `POST /v1/decisions/batch` — up to 100 concurrent decisions via asyncio.gather |
| **Drift Monitoring** | Kolmogorov-Smirnov test on rolling decision windows |
| **Observability** | Prometheus `/metrics` endpoint, structured JSON logs |
| **Python SDK** | `FairGuardClient` with retries, async variant, batch support |

---

## ⚡ Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone & Install

```bash
git clone https://github.com/your-org/fairguard.git
cd fairguard

# Backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install
```

### 2. Configure

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set JWT_SECRET at minimum
```

### 3. Run

```bash
# Terminal 1 — Backend API
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend Dashboard
cd frontend
npm run dev
```

Open `http://localhost:5173` for the dashboard or `http://localhost:8000/docs` for the interactive API.

### 4. SDK — 5 lines of code

```python
from fairguard_sdk import FairGuardClient

client = FairGuardClient(api_key="sk_fgt_your_key")
result = client.evaluate(
    applicant_features={"age": 35, "income": 55000, "sex": "Female"},
    model_output={"decision": "denied", "confidence": 0.73},
    protected_attributes=["sex"],
    domain="lending",
)
print(result["corrected_decision"])  # {"decision": "approved", ...}
print(result["explanation"])         # EU AI Act Article 14 compliant explanation
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FairGuard System                        │
│                                                             │
│  ┌───────────┐    ┌──────────────────────────────────────┐  │
│  │ Next.js   │    │         FastAPI Backend               │  │
│  │ Dashboard │◄──►│                                      │  │
│  │ (Port 5173│    │  ┌─────────┐  ┌──────────────────┐  │  │
│  └───────────┘    │  │  Auth   │  │  Decision Router  │  │  │
│                   │  │  RBAC   │  │  /v1/decision     │  │  │
│  ┌───────────┐    │  └─────────┘  └────────┬─────────┘  │  │
│  │ Python SDK│    │                         │            │  │
│  │ (httpx)   │───►│  ┌──────────────────────▼─────────┐  │  │
│  └───────────┘    │  │        Bias Pipeline            │  │  │
│                   │  │  BiasDetector → CausalEngine    │  │  │
│                   │  │  → Corrector  → AuditLog        │  │  │
│                   │  └──────────────────────────────── ┘  │  │
│                   │                                      │  │
│                   │  ┌──────────┐  ┌───────────────────┐ │  │
│                   │  │ SQLite / │  │  SSE Stream       │ │  │
│                   │  │ Postgres │  │  (Redis optional) │ │  │
│                   │  └──────────┘  └───────────────────┘ │  │
│                   └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Hash-chain audit log** | Tamper-evident audit trail; each record SHA-256 hashes prev record |
| **Detect-only mode** | Enterprises can observe bias without automatic correction — liability preservation |
| **Domain registry** | Pluggable DAGs per industry vertical without code changes |
| **Redis optional** | In-process SSE works single-worker; Redis unlocks horizontal scaling transparently |
| **LLM explanation async** | Causal correction is sub-200ms; LLM explanation fires as BackgroundTask |

---

## 📡 API Reference

Full interactive docs: `http://localhost:8000/docs`

### Core Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/v1/decision` | any | Single bias evaluation |
| `POST` | `/v1/decisions/batch` | any | Batch evaluation (≤100) |
| `GET` | `/v1/domains` | public | List supported domains |
| `GET` | `/v1/decisions/domains` | auditor+ | Per-domain analytics |
| `GET` | `/v1/report/generate` | auditor+ | EU AI Act PDF report |
| `GET` | `/v1/report/analytics` | auditor+ | JSON compliance analytics |
| `GET` | `/v1/audit/logs` | auditor+ | Paginated audit log |
| `GET` | `/v1/audit/verify` | auditor+ | Hash-chain integrity check |
| `PUT` | `/v1/settings/thresholds` | admin | Update bias thresholds |
| `POST` | `/v1/webhooks` | admin | Register webhook URL |
| `GET` | `/v1/stream/decisions` | any | SSE real-time event stream |
| `GET` | `/v1/drift/status` | any | Drift monitoring status |
| `GET` | `/metrics` | internal | Prometheus metrics |

### Request Example

```json
POST /v1/decision
{
  "applicant_features": {"age": 28, "sex": "Female", "race": "Black", "income": 42000},
  "model_output": {"decision": "denied", "confidence": 0.81},
  "protected_attributes": ["sex", "race"],
  "domain": "lending",
  "mode": "detect_and_correct"
}
```

### Response Example

```json
{
  "original_decision": {"decision": "denied", "confidence": 0.81},
  "corrected_decision": {"decision": "approved", "confidence": 0.81},
  "bias_detected": true,
  "bias_scores": {
    "dpd": 0.18,
    "eod": 0.14,
    "icd": 0.22,
    "cas": 0.31
  },
  "correction_applied": true,
  "causal_paths": {
    "sex":  ["sex → occupation → capital-gain → decision"],
    "race": ["race → occupation → capital-gain → decision"]
  },
  "domain": "lending",
  "explanation": "Bias detected across sex and race attributes (CAS: 0.31). Counterfactual correction applied per EU AI Act Article 14."
}
```

---

## 🏢 Multi-Domain Support

FairGuard includes a **domain registry** with pre-configured causal DAGs:

```python
# Discover available domains
GET /v1/domains

# Use a specific domain
POST /v1/decision
{"domain": "healthcare", ...}
```

To add a custom domain:

```python
# backend/app/services/domain_registry.py
from app.services.domain_registry import DomainConfig, DOMAINS

DOMAINS["my_domain"] = DomainConfig(
    name="my_domain",
    description="Custom scoring domain",
    dag_edges=[("feature_a", "outcome"), ("protected_attr", "outcome")],
    protected_attrs=["protected_attr"],
    decision_vocab=["approve", "deny"],
    causal_paths={"protected_attr": ["protected_attr → outcome (direct)"]},
    default_row={"feature_a": 0.5, "protected_attr": "Group A"},
    ace_fallbacks={"protected_attr": 0.15},
)
```

---

## 🔒 RBAC & Security

FairGuard enforces role-based access across all routes:

| Role | Capabilities |
|---|---|
| `admin` | Full access — thresholds, webhooks, reports, decisions |
| `auditor` | Read-only — reports, audit logs, analytics |
| `viewer` | Decision submission only |

Tokens are issued at `POST /v1/auth/token`. Role is embedded in the JWT payload.

### Audit Chain Verification

Every decision is SHA-256 hashed with the previous record's hash:

```
record_hash = SHA256(prev_hash + JSON.dumps(record, sort_keys=True))
```

Verify chain integrity: `GET /v1/audit/verify` returns `{valid, records_checked, first_invalid_id}`.

---

## 📊 Compliance Reporting

```python
# Download EU AI Act PDF
client.download_compliance_report("report_q1_2025.pdf")

# Or hit the API
GET /v1/report/generate   → PDF
GET /v1/report/analytics  → JSON
```

Report sections:
1. Executive Summary with compliance gauge
2. Domain-specific bias breakdown
3. 7-day intervention trend
4. EU AI Act Article mapping (Art. 10, 12, 13, 14)
5. Hash-chain integrity status
6. Auto-generated recommendations

---

## 🔔 Webhooks

Register a URL to receive real-time bias events:

```bash
curl -X POST /v1/webhooks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"url": "https://your.app/hooks/bias", "events": ["bias.detected", "drift.detected"]}'
```

Events are HMAC-SHA256 signed with your webhook secret. Verify with:

```python
import hmac, hashlib
expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
assert request.headers["X-FairGuard-Sig"] == expected
```

---

## 📈 Observability

FairGuard exposes a Prometheus `/metrics` endpoint when `prometheus-fastapi-instrumentator` is installed:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: fairguard
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
```

Metrics include: request latency histograms, error rates, endpoint hit counts.

---

## 🐳 Docker

```bash
docker compose up -d
```

Starts: `fairguard-api` (port 8000) + `fairguard-frontend` (port 5173).

For Redis-backed SSE (multi-worker):

```bash
REDIS_URL=redis://redis:6379/0 docker compose up -d
```

---

## 🧪 Testing

```bash
# Run all tests from repo root
pytest -v

# With coverage
pytest --cov=backend/app --cov-report=html

# Load test (requires running server)
locust -f locustfile.py --host=http://localhost:8000
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repo
2. Create your branch: `git checkout -b feature/my-feature`
3. Run tests: `pytest -v`
4. Submit a PR — CI will run automatically

### Development Setup

```bash
# Install dev extras
pip install -r backend/requirements.txt
pre-commit install

# Format
black backend/
ruff check backend/

# Type check
mypy backend/app
```

---

## 📋 Roadmap

- [ ] JavaScript/TypeScript SDK (`@fairguard/sdk`)
- [ ] A/B testing on correction strategies
- [ ] OpenTelemetry tracing integration
- [ ] Model versioning and rollback
- [ ] Usage metering and billing API
- [ ] Developer portal with onboarding wizard
- [ ] PyPI package (`pip install fairguard-sdk`)

---

## 📜 Regulatory Context

FairGuard is designed around EU AI Act obligations for **high-risk AI systems**:

| Article | Requirement | FairGuard Feature |
|---|---|---|
| Art. 10 | Data governance | Protected attribute tracking + domain registry |
| Art. 12 | Record keeping | Immutable SHA-256 hash-chain audit log |
| Art. 13 | Transparency | Causal explanations per decision |
| Art. 14 | Human oversight | Detect-only mode, webhook alerting |

> **Disclaimer:** FairGuard is a technical tool to assist with fairness compliance. It does not constitute legal advice. Consult your Data Protection Officer for regulatory obligations specific to your jurisdiction.

---

## 📄 License

MIT © 2025 FairGuard Contributors — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ for responsible AI · <a href="http://localhost:8000/docs">API Docs</a> · <a href="https://github.com/your-org/fairguard/issues">Issues</a>
</div>
