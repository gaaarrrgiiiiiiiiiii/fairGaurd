# Contributing to FairGuard

Thank you for considering contributing to FairGuard! 🎉

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 20+
- Docker & Docker Compose (optional, for full-stack testing)

### Local Setup

```bash
# 1. Clone
git clone https://github.com/yourorg/fairguard.git
cd fairguard

# 2. Backend
cd backend
pip install -r requirements.txt

# 3. Prepare ML data
cd ../data
python prep_adult_data.py

# 4. Run backend
cd ../backend
uvicorn app.main:app --reload

# 5. Frontend (new terminal)
cd ../frontend
npm install
npm run dev
```

## Development Workflow

### Running Tests
```bash
# From repo root
pytest tests/ -v --cov=backend/app
```

### TypeScript Type Check
```bash
cd frontend
npx tsc --noEmit
```

### Linting
```bash
# Backend
pip install ruff
ruff check backend/

# Frontend
npm run lint
```

## Pull Request Guidelines

1. **One concern per PR** — keep changes focused.
2. **Tests required** — all new logic needs test coverage.
3. **Type everything** — no `Any` in Python without a comment; no `any` in TypeScript.
4. **Update the CHANGELOG** in your PR description.

## Project Architecture

| Component | Location | Purpose |
|-----------|----------|---------|
| API Backend | `backend/app/` | FastAPI endpoints |
| Bias Detector | `backend/app/services/bias_detector.py` | DPD/EOD/ICD/CAS metrics |
| Causal Engine | `backend/app/services/causal_engine.py` | DoWhy causal inference |
| Corrector | `backend/app/services/corrector.py` | Counterfactual + LLM fix |
| Frontend | `frontend/src/` | React + TypeScript dashboard |
| SDK | `sdk/` | Python client library |
| Tests | `tests/` | pytest suite |

## Code of Conduct

Be respectful, inclusive, and constructive in all project spaces.
