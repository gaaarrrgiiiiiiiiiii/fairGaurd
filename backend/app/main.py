from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import decisions, health, report, drift
from app.models.database import init_db
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
@app.on_event("startup")
async def startup_event():
    init_db()

# Include Routers
app.include_router(health.router, tags=["Health"])
app.include_router(decisions.router, prefix=settings.API_V1_STR, tags=["Decisions"])
app.include_router(report.router, prefix=f"{settings.API_V1_STR}/report", tags=["Compliance"])
app.include_router(drift.router, prefix=f"{settings.API_V1_STR}/drift", tags=["Drift"])
