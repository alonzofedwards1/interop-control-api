"""Pydantic models for health endpoints."""
from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Simple liveness payload returned by the service health endpoint."""

    status: str
    service: str
    environment: str
