from __future__ import annotations

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Header, Request, Response, status

from app.config.settings import Settings, get_settings
from app.pd.storage import PDStorage

router = APIRouter()


@router.post("/callback")
async def patient_discovery_callback(
    request: Request,
    settings: Settings = Depends(get_settings),
    x_correlation_id: str | None = Header(default=None),
) -> Response:
    correlation_id = x_correlation_id or str(uuid.uuid4())
    storage = PDStorage()

    raw_body = await request.body()
    content_type = request.headers.get("content-type", "")
    received_at = datetime.utcnow().isoformat()

    payload_text = raw_body.decode("utf-8", errors="ignore")
    payload_type = "xml" if "xml" in content_type.lower() else "json"

    message_type = "UNKNOWN"
    if "PRPA_IN201305" in payload_text:
        message_type = "PRPA_IN201305UV02"
    elif "PRPA_IN201306" in payload_text:
        message_type = "PRPA_IN201306UV02"

    storage.save_pd_response(
        correlation_id=correlation_id,
        payload=payload_text,
        payload_type=payload_type,
        message_type=message_type,
    )

    storage.update_execution(
        correlation_id=correlation_id,
        update={
            "status": "RESPONSE_RECEIVED",
            "message_type": message_type,
            "received_at": received_at,
        },
    )

    return Response(
        status_code=status.HTTP_202_ACCEPTED,
        content="ACK",
    )
