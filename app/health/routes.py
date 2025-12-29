"""Health and observability endpoints."""
from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    """Simple liveness endpoint consumed by infrastructure health checks."""

    return {"status": "ok", "service": settings.service_name, "environment": settings.environment}
