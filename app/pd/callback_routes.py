from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Header, Request, status
from fastapi.responses import JSONResponse

from app.pd.storage import PDStorage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/callback")
@router.post("/callback/")
async def patient_discovery_callback(
    request: Request,
    x_correlation_id: str | None = Header(default=None),
) -> JSONResponse:
    raw_body = await request.body()
    payload_text = raw_body.decode("utf-8", errors="ignore")

    payload_json: dict | None = None
    try:
        payload_json = json.loads(payload_text) if payload_text else None
    except json.JSONDecodeError:
        payload_json = None

    correlation_id = x_correlation_id
    if not correlation_id and isinstance(payload_json, dict):
        correlation_id = payload_json.get("correlation_id") or payload_json.get("correlationId")

    correlation_id = correlation_id or str(uuid.uuid4())
    received_at = datetime.utcnow().isoformat()

    content_type = request.headers.get("content-type", "")
    payload_type = "xml" if "xml" in content_type.lower() else "json"

    message_type = "UNKNOWN"
    if "PRPA_IN201305" in payload_text:
        message_type = "PRPA_IN201305UV02"
    elif "PRPA_IN201306" in payload_text:
        message_type = "PRPA_IN201306UV02"

    logger.info(
        "PD callback received",
        extra={
            "correlation_id": correlation_id,
            "payload": payload_text,
            "payload_type": payload_type,
            "received_at": received_at,
        },
    )

    storage = PDStorage()
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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "received", "correlation_id": correlation_id},
    )
