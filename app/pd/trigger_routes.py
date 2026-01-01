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

    correlation_id = str(uuid.uuid4())
    storage = PDStorage()

    storage.create_execution(
        correlation_id=correlation_id,
        patient_reference=patient_reference,
        status="TRIGGERED",
        triggered_at=datetime.utcnow().isoformat(),
    )

    payload = {
        "patient_reference": patient_reference,
        "callback_url": settings.pd_callback_url,
        "correlation_id": correlation_id,
    }

    try:
        response = await send_pd_request(
            endpoint_url=settings.pd_endpoint_url,
            payload=payload,
        )

        storage.update_execution(
            correlation_id,
            {
                "status": "FORWARDED",
                "forwarded_at": datetime.utcnow().isoformat(),
                "pd_endpoint_url": settings.pd_endpoint_url,
                "status_code": response.status_code,
            },
        )

        print("✅ Mirth trigger sent")

    except Exception as e:
        print("❌ MIRTH POST FAILED:", str(e))

        storage.update_execution(
            correlation_id,
            {
                "status": "FAILED",
                "error": str(e),
                "pd_endpoint_url": settings.pd_endpoint_url,
            },
        )
        return {
            "correlation_id": correlation_id,
            "forwarded": False,
            "error": str(e),
        }

    return {
        "correlation_id": correlation_id,
        "forwarded": True,
    }
