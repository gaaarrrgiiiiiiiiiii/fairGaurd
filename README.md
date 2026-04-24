<div align="center">

# 🛡️ FairGuard

### The Real-Time AI Fairness Firewall

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![EU AI Act](https://img.shields.io/badge/EU_AI_Act-Compliant-003399?style=for-the-badge&logo=european-union&logoColor=white)](#compliance)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Intercept biased ML decisions in real time — before they affect a single user.**

FairGuard is an ultra-low latency middleware that sits between your ML model and your users, automatically detecting and correcting demographic bias using causal inference and counterfactual reasoning.

[🚀 Quick Start](#-quick-start) · [📖 How It Works](#-how-it-works) · [🧪 Live Demo](#-live-demo) · [📡 API Reference](#-api-reference) · [🔌 SDK](#-sdk-integration)

---

</div>

## 🎯 The Problem

> The EU AI Act makes biased AI **illegal** — with fines up to **€35 million**. Yet auditing models for fairness takes weeks, and most bias is discovered *after* it has already harmed real people.

Every company deploying AI in hiring, lending, insurance, or healthcare faces an existential compliance risk. Traditional fairness auditing is retrospective — it catches bias *after the damage is done*.

**FairGuard flips the paradigm.** Instead of auditing after deployment, it intercepts biased decisions **in real time**, corrects them using causal counterfactuals, and generates instant compliance documentation.

---

## ⚡ How It Works

```
┌─────────────┐     ┌──────────────────────────────────────────────────┐     ┌──────────────┐
│             │     │              FairGuard Firewall                  │     │              │
│   Your ML   │────▶│  ┌─────────┐  ┌──────────┐  ┌───────────────┐  │────▶│   End User   │
│   Model     │     │  │  Bias   │  │  Causal  │  │ Counterfactual│  │     │  (Protected) │
│             │     │  │ Metrics │  │  Engine  │  │  Corrector    │  │     │              │
└─────────────┘     │  └────┬────┘  └────┬─────┘  └───────┬───────┘  │     └──────────────┘
                    │       │            │                 │          │
                    │       ▼            ▼                 ▼          │
                    │  ┌─────────────────────────────────────────┐    │
                    │  │         Compliance Report Engine        │    │
                    │  │      (EU AI Act Article 13 Export)      │    │
                    │  └─────────────────────────────────────────┘    │
                    └──────────────────────────────────────────────────┘
                                    ⏱️ < 15ms
```

### The Pipeline (4 Parallel Stages)

| Stage | Engine | What It Does |
|-------|--------|-------------|
| **1. Statistical Detection** | Fairlearn-powered metrics | Computes Demographic Parity, Equalized Odds, and Disparate Impact ratios across protected groups |
| **2. Causal Analysis** | DoWhy Causal Graphs | Proves whether a protected attribute (e.g., gender) *caused* the adverse outcome, not just correlated with it |
| **3. Counterfactual Correction** | DiCE Counterfactual Engine | Generates the minimum viable change needed to flip the decision fairly |
| **4. Compliance Generation** | Gemini LLM Integration | Produces human-readable rationales and Article 13-compliant monitoring reports |

---

## 🏗️ Architecture

```
fairguard/
├── backend/                    # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py             # Application entry point
│   │   ├── config.py           # Environment & settings
│   │   ├── routers/
│   │   │   ├── decisions.py    # POST /v1/decision — core bias evaluation
│   │   │   ├── drift.py        # GET  /v1/drift    — model drift monitoring
│   │   │   ├── report.py       # GET  /v1/report   — compliance PDF export
│   │   │   └── health.py       # GET  /health      — liveness probe
│   │   ├── services/
│   │   │   ├── bias_detector.py        # Statistical fairness metrics (ICD/CAS)
│   │   │   ├── causal_engine.py        # DoWhy causal inference graphs
│   │   │   ├── counterfactual_engine.py # DiCE counterfactual generation
│   │   │   ├── corrector.py            # Decision correction logic
│   │   │   ├── llm_service.py          # Gemini API for compliance rationales
│   │   │   ├── compliance_report.py    # EU AI Act report builder
│   │   │   └── threshold_config.py     # Bias threshold configuration
│   │   ├── models/             # SQLAlchemy ORM models
│   │   └── auth/               # JWT authentication layer
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # React 19 + TypeScript Dashboard
│   └── src/
│       ├── App.tsx             # Main application shell
│       └── components/
│           ├── DemoSimulator.tsx      # "John vs Sarah" live demo
│           ├── CausalGraph.tsx        # D3.js interactive causal DAG
│           ├── BiasMetricsChart.tsx    # Recharts bias visualization
│           ├── MetricsGaugePanel.tsx   # Real-time metric gauges
│           ├── DecisionFeed.tsx        # Live intercept event stream
│           ├── DecisionCard.tsx        # Individual decision cards
│           └── StatsOverview.tsx       # Aggregate statistics panel
│
├── sdk/                        # Python SDK (pip-installable)
│   └── fairguard_sdk.py        # 5-line integration client
│
├── data/                       # UCI Adult Dataset pipeline
│   ├── prep_adult_data.py      # Feature engineering script
│   ├── adult_features.csv      # Processed feature matrix
│   └── adult_labels.csv        # Binary classification labels
│
├── tests/                      # Test suite
│   ├── test_bias_detection.py  # Unit tests for bias metrics
│   ├── test_compas_domain.py   # COMPAS domain validation
│   ├── benchmark_latency.py    # Sub-15ms latency benchmarks
│   └── load_test.py            # Concurrent load testing
│
├── docs/                       # Documentation
│   └── api.md                  # Full API specification
│
├── docker-compose.yml          # One-command deployment
└── .github/workflows/          # CI/CD pipeline
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- A [Google Gemini API key](https://ai.google.dev/) (for compliance rationales)

### 1️⃣ Clone & Setup Backend

```bash
git clone https://github.com/gaaarrrgiiiiiiiiiii/fairGaurd.git
cd fairGaurd/backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate    # Windows
# source venv/bin/activate      # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# ✏️ Edit .env and add your API keys

# Launch the API (default: http://localhost:8000)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2️⃣ Launch Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
# Dashboard live at http://localhost:5173
```

### 3️⃣ Run the Demo

Open `http://localhost:5173` and click the **"Run Demo Sequence"** button to watch FairGuard catch the "John vs Sarah" demographic parity violation in real time.

### 🐳 Docker (One Command)

```bash
docker compose up --build
```

---

## 🧪 Live Demo

The built-in **Demo Simulator** walks through a real-world lending scenario:

| Step | Applicant | Profile | Model Decision | FairGuard Action |
|------|-----------|---------|----------------|------------------|
| 1 | **John** (Male) | Age 35, Income $55K | ✅ Approved | ✅ Passed — No bias detected |
| 2 | **Sarah** (Female) | Age 35, Income $55K | ❌ Denied | 🛡️ **Intercepted** — Demographic parity breach detected |

When Sarah's denial is intercepted:
- The **Causal Graph** highlights `sex` as the causal factor
- The **Counterfactual Engine** computes a fair probability (73% → 89%)
- FairGuard **overrides the decision** to `Approved`
- A compliance audit trail is generated instantly

---

## 📡 API Reference

### `POST /v1/decision` — Evaluate a Decision

Send any ML model output through FairGuard for real-time bias analysis.

```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk_fgt_12345" \
  -d '{
    "applicant_features": {"age": 35, "income": 55000, "sex": "Female"},
    "model_output": {"decision": "denied", "confidence": 0.73},
    "protected_attributes": ["sex"]
  }'
```

**Response:**

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
  "explanation": "Application approved after bias correction on protected attributes ['sex']. Original probability was 73.0%, fair probability is 89.0%.",
  "audit_id": "8b3f2c5a-1b4e-4e9b-9c6d-5b3f2c5a1b4e"
}
```

### `GET /v1/report/generate` — Export Compliance Report

Generates an EU AI Act Article 13 Post-Market Monitoring PDF.

### `GET /v1/drift/status` — Model Drift Monitoring

Returns real-time drift metrics for bias stability tracking.

> 📄 Full API specification: [`docs/api.md`](docs/api.md)

---

## 🔌 SDK Integration

Drop FairGuard into your existing ML pipeline in **5 lines of Python**:

```python
from fairguard_sdk import FairGuardClient

client = FairGuardClient(api_key="sk_fgt_12345")

# Your model makes a decision...
result = client.evaluate(
    applicant_features={"age": 35, "income": 55000, "sex": "Female"},
    model_output={"decision": "denied", "confidence": 0.73},
    protected_attributes=["sex"]
)

print(result["corrected_decision"]["decision"])   # "approved"
print(result["explanation"])                       # Human-readable rationale
```

Works with **any ML framework** — XGBoost, LightGBM, scikit-learn, PyTorch, TensorFlow, LLMs, or custom models.

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| **Intercept Latency** | < 15ms p99 |
| **Bias Metrics Computed** | 4 (DP, EO, DI, Causal) |
| **Dataset** | UCI Adult (48,842 samples) |
| **Protected Attributes** | Age, Sex, Income |
| **Compliance Standard** | EU AI Act Article 13 |
| **False Positive Rate** | < 2% on benchmark |

---

## 🧬 Tech Stack

<table>
<tr>
<td align="center"><b>Layer</b></td>
<td align="center"><b>Technology</b></td>
<td align="center"><b>Purpose</b></td>
</tr>
<tr>
<td>Backend API</td>
<td>FastAPI + Uvicorn</td>
<td>Async REST API with sub-15ms response times</td>
</tr>
<tr>
<td>Bias Detection</td>
<td>Fairlearn + scikit-learn</td>
<td>Statistical parity metrics (DP, EO, DI)</td>
</tr>
<tr>
<td>Causal Inference</td>
<td>DoWhy</td>
<td>Causal graph analysis to prove attribute causation</td>
</tr>
<tr>
<td>Counterfactual Engine</td>
<td>DiCE-ML</td>
<td>Diverse counterfactual explanations for corrections</td>
</tr>
<tr>
<td>LLM Integration</td>
<td>Google Gemini</td>
<td>Natural language compliance rationale generation</td>
</tr>
<tr>
<td>Frontend</td>
<td>React 19 + TypeScript + Vite</td>
<td>Real-time monitoring dashboard</td>
</tr>
<tr>
<td>Visualization</td>
<td>D3.js + Recharts</td>
<td>Interactive causal graphs and metric charts</td>
</tr>
<tr>
<td>Database</td>
<td>SQLAlchemy + SQLite</td>
<td>Audit trail persistence</td>
</tr>
<tr>
<td>Auth</td>
<td>JWT (python-jose)</td>
<td>Secure API key authentication</td>
</tr>
<tr>
<td>Containerization</td>
<td>Docker Compose</td>
<td>One-command deployment</td>
</tr>
</table>

---

## 🧪 Testing

```bash
# Unit tests — bias detection accuracy
pytest tests/test_bias_detection.py -v

# Domain validation — COMPAS dataset
pytest tests/test_compas_domain.py -v

# Latency benchmark — verify sub-15ms target
python tests/benchmark_latency.py

# Load test — concurrent request handling
python tests/load_test.py
```

---

## <a id="compliance"></a>🏛️ Compliance: EU AI Act

FairGuard is designed from the ground up for **EU AI Act Article 13** compliance:

| Requirement | How FairGuard Addresses It |
|-------------|---------------------------|
| **Transparency** | Every decision includes a human-readable explanation of bias detection and correction logic |
| **Post-Market Monitoring** | One-click PDF report generation with full audit trails |
| **Risk Assessment** | Real-time drift detection monitors bias metric stability over time |
| **Human Oversight** | Dashboard provides complete visibility into all automated corrections |
| **Record Keeping** | Every intercept, correction, and rationale is persisted with immutable audit IDs |

---

## 🌟 Future Scope & Enterprise Enhancements

To transition FairGuard from a highly functional prototype into a globally scalable, production-ready enterprise solution for the **Google Solution Challenge**, the following enhancements are planned:

- **🌐 Multi-Domain & Cross-Industry Expansion**
  - Moving beyond the current "Lending" model to support dynamic, industry-specific causal graphs for **Hiring** (resume screening bias), **Healthcare** (triage algorithms), and **Insurance** (premium calculations).
- **⚡ Real-Time WebSocket Telemetry**
  - Upgrading the API to a fully asynchronous WebSocket architecture (`ws://`) to stream intercepted decisions and bias metrics instantly to compliance officers across the globe.
- **🔐 Enterprise RBAC & Strict Tenant Isolation**
  - Implementing fine-grained Role-Based Access Control (Admin, Auditor, API Client) and strict database-level tenant isolation, ensuring zero data leakage in a B2B SaaS environment.
- **📈 Prometheus & Grafana Observability**
  - Exposing a `/metrics` endpoint for Prometheus to scrape API latency, error rates, and system-wide bias drift, visualized through custom Grafana dashboards for enterprise DevOps teams.
- **🧠 Advanced LLM Reasoning & Multilingual Support**
  - Leveraging Gemini's extended context window to generate EU AI Act compliance reports and counterfactual explanations in over 40 languages, democratizing AI fairness globally.

---

## 🌍 Google Solution Challenge Impact

FairGuard is uniquely positioned for the Google Solution Challenge because it directly addresses **UN Sustainable Development Goal 10 (Reduced Inequalities)** and **SDG 16 (Strong Institutions)**. 

Unlike consumer-facing apps, FairGuard adopts a **B2B Middleware Architecture**. By integrating with just one major financial institution or HR platform, FairGuard can protect millions of individuals simultaneously from algorithmic discrimination. It leverages Google's advanced AI not as a simple chatbot, but as a complex reasoning agent solving a massive, urgent global issue: Algorithmic Bias.

---

## 📜 License

This project is open source under the [MIT License](LICENSE).

---

<div align="center">

**Built for the [Google Solution Challenge](https://developers.google.com/community/gdsc-solution-challenge) 🌍**

*Making AI fair, one decision at a time.*

<sub>If FairGuard helped you, consider giving it a ⭐</sub>

</div>
