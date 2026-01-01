from __future__ import annotations

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException

from app.config.settings import Settings, get_settings
from app.pd.storage import PDStorage
from app.pd.mirth_client import send_pd_request

router = APIRouter(prefix="/api/pd", tags=["patient-discovery"])


@router.post("/trigger/")
async def trigger_patient_discovery(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict:
    body = await request.json()
    patient_reference = body.get("patient_reference")

    if not patient_reference:
        raise HTTPException(status_code=400, detail="patient_reference is required")

    if not settings.pd_endpoint_url:
        raise HTTPException(
            status_code=500,
            detail="pd_endpoint_url is not configured",
        )

    correlation_id = str(uuid.uuid4())
    storage = PDStorage()

    storage.create_execution(
        correlation_id=correlation_id,
        patient_reference=patient_reference,
        status="TRIGGERED",
        triggered_at=datetime.utcnow().isoformat(),
    )

    try:
        print("📡 Posting PD trigger to Mirth:", settings.pd_endpoint_url)

        await send_pd_request(
            endpoint_url=settings.pd_endpoint_url,
            payload={
                "patient_reference": patient_reference,
                "correlation_id": correlation_id,
            },
        )

        print("✅ Mirth trigger sent")

    except Exception as e:
        print("🔥 MIRTH CALL FAILED:", repr(e))
        return {
            "correlation_id": correlation_id,
            "forwarded": False,
            "error": str(e),
        }

    return {
        "correlation_id": correlation_id,
        "forwarded": True,
    }
