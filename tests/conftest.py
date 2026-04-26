"""
Shared pytest configuration and fixtures for the FairGuard test suite.

Import resolution:
  pytest.ini sets `pythonpath = backend`, so `from app.xxx import yyy`
  works without any sys.path manipulation here.

Database:
  DATABASE_URL must be set BEFORE any app module is imported (because
  database.py reads it at module-load time). We use os.environ[] (not
  setdefault) so that a CI-injected DATABASE_URL always wins.
"""
import os
import sys
import tempfile
import pytest

# ---------------------------------------------------------------------------
# Environment — must happen BEFORE any app import
# ---------------------------------------------------------------------------
# Use an absolute temp path so the DB file is always writable (CI + local)
_tmp_db = os.path.join(tempfile.gettempdir(), "test_fairguard.db")

# CI may inject DATABASE_URL; respect it. Otherwise use the temp file.
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_db}")
os.environ.setdefault("FAIRGUARD_DATA_DIR", tempfile.gettempdir())
os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-characters-long")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5173")
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
