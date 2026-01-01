"""System health endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
def health_check(settings: Settings = Depends(get_settings)) -> dict:
    """
    High-level system health endpoint.

    Answers:
    - Is the API running?
    - Is configuration loaded?
    """

    return {
        "status": "ok",
        "service": "interop-control-api",
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ping")
def ping() -> dict:
    return {"status": "ok"}


@router.get("/debug/settings")
def debug_settings():
    s = get_settings()
    return {
        "auth_mode": s.auth_mode,
        "oauth_token_url": s.oauth_token_url,
        "pd_endpoint_url": s.pd_endpoint_url,
    }
