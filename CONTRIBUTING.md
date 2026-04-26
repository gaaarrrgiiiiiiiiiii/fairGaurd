# Contributing to FairGuard

Thank you for your interest! FairGuard welcomes contributions that improve fairness, performance, or usability.

## Quick Start

```bash
git clone https://github.com/your-org/fairguard.git
cd fairguard

# Backend
cd backend && pip install -r requirements.txt
cp ../.env.example ../.env  # fill in values

# Run tests
cd .. && pytest tests/ -v

# Frontend
cd frontend && npm install && npm run dev
```

## How to Contribute

### 1. Pick an Issue

- Browse [Issues](../../issues) — look for `good first issue` or `help wanted`
- Comment on the issue before starting to avoid duplicate work

### 2. Branch & Code

```bash
git checkout -b feat/your-feature-name   # feature
git checkout -b fix/bug-description      # bug fix
```

**Conventions:**
- Python: [PEP 8](https://peps.python.org/pep-0008/) — run `ruff check .` before committing
- TypeScript: ESLint + strict mode — run `npx tsc --noEmit`
- Commit messages: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`

### 3. Test

```bash
# Backend (required — must pass before PR)
pytest tests/ -v --cov=backend/app

# Frontend type check
cd frontend && npx tsc --noEmit
```

All tests must pass. New features should include tests.

### 4. Pull Request

- Target branch: `main`
- Fill in the PR template (auto-loaded)
- Link to the related issue
- Ensure CI is green before requesting review

## Architecture Overview

```
backend/app/
├── routers/      # FastAPI endpoints (decisions, drift, report, stream, auth)
├── services/     # Core engines (bias_detector, causal_engine, corrector, llm_service)
├── models/       # SQLAlchemy ORM + audit log functions
└── auth/         # JWT handling

frontend/src/
├── components/   # React UI components
├── hooks/        # useSSE, useAnalytics
└── services/     # API client (api.ts)
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SSE over WebSocket | Simpler, proxy-friendly, sufficient for one-way push |
| SQLite default | Zero-config dev; switch `DATABASE_URL` for Postgres |
| Fire-and-forget LLM | Keeps decision latency <50ms; explanation arrives async |
| In-process pub/sub | Sufficient for single-worker; swap for Redis in multi-worker |

## Reporting Security Issues

**Do not open a public issue.** Email `security@fairguard.ai` with details.
We respond within 48 hours.

## Code of Conduct

Be respectful and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) if present.

## License

By contributing, you agree your code will be released under the [MIT License](LICENSE).
