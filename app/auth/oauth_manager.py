"""OAuth2 password grant manager with in-memory caching."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from fastapi import HTTPException, status

from app.auth.models import ManualTokenRequest, OAuthCredentials, TokenCache, TokenHealth, TokenResponse


class OAuthManager:
    """Manage OAuth2 password grant tokens with proactive refreshes."""

    def __init__(self, expires_soon_seconds: int = 120, credentials: Optional[OAuthCredentials] = None) -> None:
        self._lock = asyncio.Lock()
        self._token_cache: Optional[TokenCache] = None
        self._credentials: Optional[OAuthCredentials] = credentials
        self._expires_soon_seconds = expires_soon_seconds

    async def set_credentials(self, request: ManualTokenRequest) -> TokenResponse:
        """Replace credentials and immediately fetch a token."""

        async with self._lock:
            self._credentials = OAuthCredentials(**request.model_dump())
            self._token_cache = None
        return await self._request_new_token()

    async def get_token(self) -> TokenResponse:
        """Return a valid token, refreshing when necessary."""

        async with self._lock:
            if self._token_cache and not self._is_expired(self._token_cache) and not self._expires_soon(self._token_cache):
                return TokenResponse(
                    access_token=self._token_cache.access_token,
                    token_type=self._token_cache.token_type,
                    expires_at=self._token_cache.expires_at,
                    scope=self._token_cache.scope,
                )

        # Refresh outside the lock to avoid blocking other coroutines while performing I/O.
        return await self._request_new_token()

    async def _request_new_token(self) -> TokenResponse:
        if not self._credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth2 credentials are not configured. Submit them via /api/auth/token/manual or environment variables.",
            )

        async with self._lock:
            credentials = self._credentials

        async with httpx.AsyncClient(timeout=30.0) as client:
            data = {
                "grant_type": "password",
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "username": credentials.username,
                "password": credentials.password,
            }
            if credentials.scope:
                data["scope"] = credentials.scope

            response = await client.post(credentials.token_url, data=data)

        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "message": "Failed to obtain OAuth2 token",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        payload = response.json()
        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="OAuth2 provider did not return an access_token.",
            )

        expires_at = self._calculate_expiry(expires_in)

        token_cache = TokenCache(
            access_token=access_token,
            token_type=payload.get("token_type", "bearer"),
            scope=payload.get("scope"),
            expires_at=expires_at,
            raw_response=payload,
        )

        async with self._lock:
            self._token_cache = token_cache

        return TokenResponse(
            access_token=token_cache.access_token,
            token_type=token_cache.token_type,
            expires_at=token_cache.expires_at,
            scope=token_cache.scope,
        )

    def token_health(self) -> TokenHealth:
        """Summarize token status for health endpoints."""

        if not self._token_cache:
            return TokenHealth(token_present=False, expires_at=None, expires_in_seconds=None, expires_soon=False)

        now = datetime.now(timezone.utc)
        expires_in_seconds = int((self._token_cache.expires_at - now).total_seconds())
        return TokenHealth(
            token_present=True,
            expires_at=self._token_cache.expires_at,
            expires_in_seconds=expires_in_seconds,
            expires_soon=self._expires_soon(self._token_cache),
        )

    def _calculate_expiry(self, expires_in: Optional[int]) -> datetime:
        now = datetime.now(timezone.utc)
        if expires_in is None:
            # Default to one hour if the provider omits expires_in.
            return now + timedelta(hours=1)
        return now + timedelta(seconds=int(expires_in))

    def _is_expired(self, token: TokenCache) -> bool:
        return datetime.now(timezone.utc) >= token.expires_at

    def _expires_soon(self, token: TokenCache) -> bool:
        return (token.expires_at - datetime.now(timezone.utc)) <= timedelta(seconds=self._expires_soon_seconds)


def build_oauth_manager(settings) -> OAuthManager:
    """Factory for wiring the OAuth manager from settings."""

    credentials = None
    if settings.oauth_token_url and settings.oauth_client_id and settings.oauth_client_secret and settings.oauth_username and settings.oauth_password:
        credentials = OAuthCredentials(
            token_url=settings.oauth_token_url,
            client_id=settings.oauth_client_id,
            client_secret=settings.oauth_client_secret,
            username=settings.oauth_username,
            password=settings.oauth_password,
            scope=settings.oauth_scope,
        )
    return OAuthManager(expires_soon_seconds=settings.expires_soon_seconds, credentials=credentials)
