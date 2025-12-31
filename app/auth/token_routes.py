import jwt
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.models import (
    ManualTokenRequest,
    TokenResponse,
    TokenHealth,
    TokenDecodeRequest,
)
from app.auth.oauth_manager import OAuthManager
from app.auth.dependencies import get_oauth_manager
from app.config.settings import Settings, get_settings

router = APIRouter(prefix="/api/auth/token", tags=["auth"])


# -------------------------------------------------------------------
# Guard: Ensure SYSTEM OAuth only (no SMART yet)
# -------------------------------------------------------------------
def require_system_auth(settings: Settings = Depends(get_settings)):
    if settings.auth_mode != "system":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SMART/FHIR authentication is not enabled"
        )
    return True


# -------------------------------------------------------------------
# 1️⃣ DEFAULT: Issue token using backend environment variables
# -------------------------------------------------------------------
@router.post("", response_model=TokenResponse)
async def issue_token(
    _: bool = Depends(require_system_auth),
    manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Issue a token using backend-managed OAuth credentials.
    UI does NOT send secrets.
    SYSTEM OAuth only.
    """
    return await manager.issue_token_from_env()


# -------------------------------------------------------------------
# 2️⃣ DEBUG ONLY: Manually supply OAuth credentials
# -------------------------------------------------------------------
@router.post("/manual", response_model=TokenResponse)
async def issue_token_manual(
    request: ManualTokenRequest,
    _: bool = Depends(require_system_auth),
    manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    DEBUG ONLY.
    Issue a token using credentials supplied in the request body.
    NOT for production UI use.
    """
    return await manager.set_credentials(request)


# -------------------------------------------------------------------
# 3️⃣ Retrieve cached token
# -------------------------------------------------------------------
@router.get("", response_model=TokenResponse)
async def get_token(
    _: bool = Depends(require_system_auth),
    manager: OAuthManager = Depends(get_oauth_manager),
):
    return await manager.get_token()


# -------------------------------------------------------------------
# 4️⃣ Token health (no auth required)
# -------------------------------------------------------------------
@router.get("/health", response_model=TokenHealth)
def token_health(
    manager: OAuthManager = Depends(get_oauth_manager),
):
    return manager.token_health()


# -------------------------------------------------------------------
# 5️⃣ JWT decode (inspection only, no verification)
# -------------------------------------------------------------------
@router.post("/decode")
def decode_jwt(request: TokenDecodeRequest):
    """
    Decode JWT header & claims WITHOUT verification.
    Safe for inspection/debugging only.
    """
    try:
        header = jwt.get_unverified_header(request.token)
        claims = jwt.decode(
            request.token,
            options={
                "verify_signature": False,
                "verify_exp": False,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {"header": header, "claims": claims}
