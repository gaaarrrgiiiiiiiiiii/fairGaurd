"""Health check endpoint — used by Docker health checks and load balancers."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness probe — returns 200 OK when the service is up."""
    return HealthResponse(status="ok", version="1.0.0")
