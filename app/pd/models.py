"""Models for patient discovery orchestration."""
from pydantic import BaseModel, Field


class PatientDiscoveryRequest(BaseModel):
    """Demo-friendly patient discovery payload (non-PHI)."""

    first_name: str = Field(..., description="Patient given name used for discovery (demo data only).")
    last_name: str = Field(..., description="Patient family name used for discovery (demo data only).")
    date_of_birth: str | None = Field(None, description="Optional date of birth in YYYY-MM-DD format.")
    gender: str | None = Field(None, description="Optional gender marker for filtering.")
    city: str | None = Field(None, description="Optional city for matching context.")
    state: str | None = Field(None, description="Optional state for matching context.")


class PatientDiscoveryResponse(BaseModel):
    """Immediate response for patient discovery triggers."""

    correlation_id: str = Field(..., description="Server generated correlation identifier.")
    forwarded: bool = Field(..., description="Indicates whether the request was forwarded to the downstream endpoint.")
    downstream_status: int | None = Field(None, description="HTTP status code returned by the downstream system, when available.")
    message: str | None = Field(None, description="Additional context about downstream handling.")
