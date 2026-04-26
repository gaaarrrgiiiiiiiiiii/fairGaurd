"""
Shared pytest configuration and fixtures for the FairGuard test suite.
"""
import os
import sys
import pytest

# ---------------------------------------------------------------------------
# Ensure 'backend' is importable as 'app.*'
# ---------------------------------------------------------------------------
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ---------------------------------------------------------------------------
# Override database to a temp in-memory SQLite for tests
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_fairguard.db")
os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-characters-long")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5173")
# Enable dev-mode so tests don't need real JWT tokens
os.environ.setdefault("FAIRGUARD_DEV_MODE", "true")
os.environ.setdefault("FAIRGUARD_API_KEYS", "{}")


# ---------------------------------------------------------------------------
# FastAPI test client fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def test_client():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.models.database import init_db

    init_db()
    with TestClient(app) as client:
        yield client


# ---------------------------------------------------------------------------
# Reusable bias detector fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def detector():
    from app.services.bias_detector import BiasDetector
    return BiasDetector()
