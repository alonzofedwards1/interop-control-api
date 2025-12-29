"""Patient discovery orchestration routes."""
from __future__ import annotations

import uuid

import httpx
from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings
from app.pd.models import PatientDiscoveryRequest, PatientDiscoveryResponse

router = APIRouter(prefix="/api/pd", tags=["patient-discovery"])


@router.post("/trigger", response_model=PatientDiscoveryResponse)
async def trigger_patient_discovery(
    request: PatientDiscoveryRequest, settings: Settings = Depends(get_settings)
) -> PatientDiscoveryResponse:
    """Forward demo-friendly patient discovery payloads to a configured endpoint.

    The control plane generates and returns a correlation identifier immediately.
    Downstream forwarding is best-effort; failures are surfaced via the response body
    without persisting any patient data.
    """

    correlation_id = str(uuid.uuid4())

    if not settings.pd_endpoint_url:
        return PatientDiscoveryResponse(
            correlation_id=correlation_id,
            forwarded=False,
            downstream_status=None,
            message="pd_endpoint_url is not configured; request was not forwarded.",
        )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            downstream_response = await client.post(
                settings.pd_endpoint_url,
                json=request.model_dump(),
                headers={"X-Correlation-ID": correlation_id},
            )
        forwarded = True
        downstream_status = downstream_response.status_code
        message = "Forwarded to downstream endpoint"
    except httpx.HTTPError as exc:
        forwarded = False
        downstream_status = None
        message = f"Failed to reach downstream endpoint: {exc}"  # type: ignore[str-format]

    return PatientDiscoveryResponse(
        correlation_id=correlation_id,
        forwarded=forwarded,
        downstream_status=downstream_status,
        message=message,
    )
