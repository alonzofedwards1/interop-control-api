from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from fastapi import HTTPException

from app.auth.models import (
    ManualTokenRequest,
    OAuthCredentials,
    TokenCache,
    TokenResponse,
    TokenHealth,
)
from app.config.settings import Settings


class OAuthManager:
    """
    Manages SYSTEM OAuth tokens using OpenEMR's OAuth2 Password Grant.
    SMART / FHIR authorization flows are intentionally NOT implemented yet.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._cache: Optional[TokenCache] = None

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    async def issue_token_from_env(self) -> TokenResponse:
        """
        DEFAULT PATH.
        Issues a token using backend-managed OAuth credentials from env vars.
        Frontend MUST NOT supply secrets.
        """

        if self.settings.auth_mode != "system":
            raise HTTPException(
                status_code=403,
                detail="System OAuth is disabled by configuration",
            )

        missing = [
            name
            for name, value in {
                "OAUTH_TOKEN_URL": self.settings.oauth_token_url,
                "OAUTH_CLIENT_ID": self.settings.oauth_client_id,
                "OAUTH_CLIENT_SECRET": self.settings.oauth_client_secret,
                "OAUTH_USERNAME": self.settings.oauth_username,
                "OAUTH_PASSWORD": self.settings.oauth_password,
            }.items()
            if not value
        ]

        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Missing OAuth environment variables: {', '.join(missing)}",
            )

        creds = OAuthCredentials(
            token_url=self.settings.oauth_token_url,
            client_id=self.settings.oauth_client_id,
            client_secret=self.settings.oauth_client_secret,
            username=self.settings.oauth_username,
            password=self.settings.oauth_password,
            scope=self.settings.oauth_scope,
        )

        return await self._issue_token(creds)

    async def set_credentials(self, request: ManualTokenRequest) -> TokenResponse:
        """
        DEBUG ONLY.
        Allows issuing a token using credentials supplied in the request body.
        SHOULD NOT be enabled in production UIs.
        """
        return await self._issue_token(request)

    async def get_token(self) -> TokenResponse:
        """
        Return cached token if valid.
        """
        if not self._cache:
            raise HTTPException(status_code=404, detail="No token cached")

        if self._cache.expires_at <= datetime.now(tz=timezone.utc):
            raise HTTPException(status_code=401, detail="Cached token expired")

        return self._to_response()

    def token_health(self) -> TokenHealth:
        """
        Lightweight token health view.
        Safe to call even when no token exists.
        """
        if not self._cache:
            return TokenHealth(
                token_present=False,
                expires_at=None,
                expires_in_seconds=None,
                expires_soon=False,
            )

        now = datetime.now(tz=timezone.utc)
        remaining = int((self._cache.expires_at - now).total_seconds())

        return TokenHealth(
            token_present=True,
            expires_at=self._cache.expires_at,
            expires_in_seconds=remaining,
            expires_soon=remaining < self.settings.expires_soon_seconds,
        )

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------

    async def _issue_token(self, creds: OAuthCredentials) -> TokenResponse:
        """
        Core issuance logic shared by env + manual paths.
        """
        data = await self._fetch_token(creds)

        expires_in = int(data.get("expires_in", 0))
        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)

        self._cache = TokenCache(
            access_token=data["access_token"],
            token_type=data.get("token_type", "bearer"),
            expires_at=expires_at,
            scope=data.get("scope"),
            raw_response=data,
        )

        return self._to_response()

    def _to_response(self) -> TokenResponse:
        assert self._cache is not None

        return TokenResponse(
            access_token=self._cache.access_token,
            token_type=self._cache.token_type,
            expires_at=self._cache.expires_at,
            scope=self._cache.scope,
        )

    async def _fetch_token(self, creds: OAuthCredentials) -> dict:
        """
        Executes the OpenEMR OAuth2 Password Grant request.
        Matches the working curl request exactly.
        """

        payload = {
            "grant_type": "password",
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "username": creds.username,
            "password": creds.password,
            "user_role": "users",  # REQUIRED by OpenEMR (non-standard)
        }

        if creds.scope:
            payload["scope"] = creds.scope

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                creds.token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "OpenEMR token request failed",
                    "status": response.status_code,
                    "body": response.text[:500],
                },
            )

        raw = response.text.strip()
        json_start = raw.find("{")

        # OpenEMR sometimes emits HTML warnings before JSON
        if json_start == -1:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "OpenEMR returned non-JSON response",
                    "raw": raw[:500],
                },
            )

        try:
            data = json.loads(raw[json_start:])
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Failed to parse token JSON",
                    "error": str(e),
                },
            )

        if "access_token" not in data:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Malformed token response",
                    "response": data,
                },
            )

        return data
