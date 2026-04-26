# Contributing to FairGuard

Thank you for considering contributing! FairGuard is open-source and we welcome all contributions — bug reports, documentation improvements, new domain configs, and features.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Adding a New Domain](#adding-a-new-domain)

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please be respectful, inclusive, and constructive.

---

## How to Contribute

### 🐛 Bug Reports

Open an [issue](https://github.com/your-org/fairguard/issues) with:
- Steps to reproduce
- Expected vs actual behaviour
- Python version, OS, relevant logs

### 💡 Feature Requests

Open an issue tagged `enhancement`. Describe the use case and why it matters for fairness/compliance.

### 🔀 Pull Requests

PRs are welcome! For large changes, open an issue first to discuss the approach.

---

## Development Setup

```bash
git clone https://github.com/your-org/fairguard.git
cd fairguard

# Create and activate venv
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate   # macOS/Linux

# Install backend + dev deps
pip install -r backend/requirements.txt

# Install frontend deps
cd frontend && npm install && cd ..

# (Optional) Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Running Locally

```bash
# Backend (from repo root)
uvicorn backend.app.main:app --reload --port 8000 --app-dir .

# Or from backend/
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```

---

## Project Structure

```
fairguard/
├── backend/
│   ├── app/
│   │   ├── auth/          # JWT handling, RBAC roles
│   │   ├── models/        # SQLAlchemy ORM + Pydantic schemas
│   │   ├── routers/       # FastAPI route handlers
│   │   └── services/      # Business logic (bias, causal, correction)
│   ├── data/              # ML model + training data
│   └── requirements.txt
├── frontend/              # Next.js dashboard
├── sdk/                   # Python SDK (fairguard_sdk.py)
├── tests/                 # pytest test suite
├── .github/workflows/     # CI/CD
├── pytest.ini             # Unified test config
└── locustfile.py          # Load tests
```

---

## Testing Guidelines

All tests live in `tests/` and run from the **repo root**:

```bash
pytest -v                          # Run all tests
pytest tests/test_bias_detection.py  # Specific file
pytest --cov=backend/app --cov-report=html  # With coverage
```

### Test conventions

- Use `pytest` fixtures defined in `tests/conftest.py`
- Test files follow `test_<module>.py` naming
- Each new feature should include at minimum:
  - One happy-path test
  - One edge-case / failure-mode test

---

## Pull Request Process

1. **Branch**: Create from `main` — `git checkout -b feat/your-feature`
2. **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`, `fix:`, `docs:`, `test:`
3. **Tests**: `pytest -v` must pass
4. **Lint**: Run `black backend/ && ruff check backend/` (no errors)
5. **Docs**: Update `README.md` if adding user-facing features
6. **PR**: Open against `main`. CI runs automatically.

CI checks:
- `pytest` on Python 3.11 + 3.12
- `ruff` lint
- Docker smoke test

---

## Adding a New Domain

FairGuard's domain registry makes this straightforward:

```python
# backend/app/services/domain_registry.py

from app.services.domain_registry import DomainConfig, DOMAINS

DOMAINS["insurance"] = DomainConfig(
    name="insurance",
    description="Insurance underwriting and claims decisions.",
    dag_edges=[
        ("age",       "risk_class"),
        ("gender",    "risk_class"),
        ("health_status", "premium"),
        ("risk_class",    "decision"),
        ("premium",       "decision"),
    ],
    protected_attrs=["age", "gender"],
    decision_vocab=["approved", "declined", "referred"],
    causal_paths={
        "age":    ["age → risk_class → decision"],
        "gender": ["gender → risk_class → decision"],
    },
    default_row={
        "age": 45, "gender": "Male",
        "health_status": "good", "risk_class": "standard", "premium": 250,
    },
    ace_fallbacks={"age": 0.12, "gender": 0.09},
)
```

Then open a PR with:
- The domain config addition
- At least one test in `tests/` that validates a known-biased case for the domain
- A brief description in `README.md`'s domain table

---

## Questions?

Open an issue or start a [Discussion](https://github.com/your-org/fairguard/discussions). We're happy to help!
