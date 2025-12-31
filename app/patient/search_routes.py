from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
import httpx

from app.patient.models import PatientSearchRequest, PatientSearchResponse
from app.auth.dependencies import get_oauth_manager
from app.auth.oauth_manager import OAuthManager
from app.config.settings import Settings, get_settings

router = APIRouter(prefix="/api/patient", tags=["Patient Search"])


@router.post("/search", response_model=PatientSearchResponse)
async def search_patient(
    request: PatientSearchRequest,
    oauth: OAuthManager = Depends(get_oauth_manager),
    settings: Settings = Depends(get_settings),
):
    # 1️⃣ Ensure token exists
    token = await oauth.get_token()

    execution_id = str(uuid4())

    payload = {
        "execution_id": execution_id,
        "criteria": request.model_dump(),
        "source": "interop-control-plane",
    }

    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            settings.MIRTH_PD_TRIGGER_URL,
            json=payload,
            headers=headers,
        )

    if resp.status_code >= 300:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Failed to trigger Mirth PD",
                "mirth_status": resp.status_code,
                "response": resp.text,
            },
        )

    return PatientSearchResponse(
        status="submitted",
        execution_id=execution_id,
        criteria=request.model_dump(),
    )
