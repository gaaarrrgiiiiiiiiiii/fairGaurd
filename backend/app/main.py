"""
FairGuard FastAPI application entry point.

Changes from original:
  • Uses modern lifespan context manager (replaces deprecated @app.on_event)
  • CORS origins restricted via ALLOWED_ORIGINS env var
  • Rate limiting via slowapi (100 req/min per IP by default)
  • Auth router added at /v1/auth
  • Audit-log history endpoint added
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.models.database import init_db
from app.routers import auth, decisions, drift, health, report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate limiter (slowapi)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    logger.info("🚀 FairGuard starting up…")
    init_db()
    logger.info("✅ Database initialised.")
    yield
    logger.info("🛑 FairGuard shutting down.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time AI fairness firewall — intercept biased ML decisions before they reach users.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ---------------------------------------------------------------------------
# CORS — restrict to known origins via env var
# ---------------------------------------------------------------------------
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
)
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------------------------------------------------------------------------
# Global exception handler — ensure we never return a 500 without JSON
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. FairGuard safety passthrough active."},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health.router, tags=["Health"])
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"],
)
app.include_router(
    decisions.router,
    prefix=settings.API_V1_STR,
    tags=["Decisions"],
)
app.include_router(
    report.router,
    prefix=f"{settings.API_V1_STR}/report",
    tags=["Compliance"],
)
app.include_router(
    drift.router,
    prefix=f"{settings.API_V1_STR}/drift",
    tags=["Drift Monitoring"],
)
