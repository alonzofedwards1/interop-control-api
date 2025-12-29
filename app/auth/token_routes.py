"""FastAPI routes for OAuth2 token management."""
from __future__ import annotations

import jwt
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.models import ManualTokenRequest, TokenDecodeRequest, TokenHealth, TokenResponse
from app.auth.oauth_manager import OAuthManager, build_oauth_manager
from app.config.settings import Settings, get_settings

router = APIRouter(prefix="/api/auth/token", tags=["auth"])


def get_oauth_manager(settings: Settings = Depends(get_settings)) -> OAuthManager:
    """Provide a shared OAuth manager instance configured via settings."""

    # Build a manager per-process; in-memory cache is safe for this simple control plane.
    if not hasattr(get_oauth_manager, "_manager"):
        get_oauth_manager._manager = build_oauth_manager(settings)  # type: ignore[attr-defined]
    return get_oauth_manager._manager  # type: ignore[attr-defined]


@router.post("/manual", response_model=TokenResponse)
async def submit_credentials(
    request: ManualTokenRequest,
    manager: OAuthManager = Depends(get_oauth_manager),
) -> TokenResponse:
    """Accept credentials and immediately exchange them for an access token."""

    return await manager.set_credentials(request)


@router.get("", response_model=TokenResponse)
async def get_access_token(manager: OAuthManager = Depends(get_oauth_manager)) -> TokenResponse:
    """Return a valid access token, refreshing when it is near expiry."""

    return await manager.get_token()


@router.get("/health", response_model=TokenHealth)
async def token_health(manager: OAuthManager = Depends(get_oauth_manager)) -> TokenHealth:
    """Expose token presence and expiry metadata for observability."""

    return manager.token_health()


@router.post("/decode")
def decode_jwt(request: TokenDecodeRequest) -> dict:
    """Decode a JWT without verifying the signature or claims."""

    if not request.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token is required")

    try:
        header = jwt.get_unverified_header(request.token)
        claims = jwt.decode(request.token, options={"verify_signature": False, "verify_exp": False})
    except jwt.PyJWTError as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"header": header, "claims": claims}
