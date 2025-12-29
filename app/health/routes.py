"""Health and observability endpoints."""
from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings
from app.health.models import HealthStatus

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus)
def health(settings: Settings = Depends(get_settings)) -> HealthStatus:
    """Simple liveness endpoint consumed by infrastructure health checks."""

    return HealthStatus(status="ok", service=settings.service_name, environment=settings.environment)
