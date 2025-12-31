"""Pydantic models for health endpoints."""
from datetime import datetime
from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Simple liveness payload returned by the service health endpoint."""

    status: str
    service: str
    environment: str


class TokenHealthStatus(BaseModel):
    """Observability payload describing OAuth token state."""

    token_present: bool
    expires_at: datetime | None
    expires_in_seconds: int | None
    expires_soon: bool
