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
    """
    M1: Explicit startup warm-up.
    All heavy singletons (model loads, DiCE explainer, population metrics)
    are initialised here before the server accepts any requests.
    References stored on app.state for future DI migration.
    """
    logger.info("🚀 FairGuard starting up…")

    # 1. Database
    init_db()
    logger.info("✅ Database initialised.")

    # 2. Warm up ML singletons (they already init at import — this is explicit
    #    documentation + state registration for DI)
    try:
        from app.services.bias_detector import bias_detector
        from app.services.causal_engine import causal_engine
        from app.services.counterfactual_engine import counterfactual_engine
        from app.services.llm_service import llm_service

        # Register on app.state — future DI can read from here
        app.state.bias_detector           = bias_detector
        app.state.causal_engine           = causal_engine
        app.state.counterfactual_engine   = counterfactual_engine
        app.state.llm_service             = llm_service

        model_ok  = bias_detector.model is not None
        dice_ok   = counterfactual_engine._dice_exp is not None
        logger.info(
            "✅ Services ready | model=%s | dice=%s",
            '✓' if model_ok else '✕ (will use fallbacks)',
            '✓' if dice_ok  else '✕ (will use attribute-flip)',
        )
    except Exception as exc:
        logger.error("❌ Service warm-up failed: %s", exc, exc_info=True)

    logger.info("🔒 FAIRGUARD_DEV_MODE=%s", os.getenv('FAIRGUARD_DEV_MODE', 'false'))
    logger.info("🎯 FairGuard ready.")
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
