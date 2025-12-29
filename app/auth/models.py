"""Pydantic models for authentication endpoints and token cache."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class OAuthCredentials(BaseModel):
    """Credentials needed for OAuth2 password grant requests."""

    token_url: str = Field(..., description="OAuth2 token URL to exchange credentials.")
    client_id: str = Field(..., description="OAuth2 client identifier.")
    client_secret: str = Field(..., description="OAuth2 client secret.")
    username: str = Field(..., description="Resource owner username used for password grant.")
    password: str = Field(..., description="Resource owner password used for password grant.")
    scope: Optional[str] = Field(None, description="Optional space-delimited scopes for the token.")


class ManualTokenRequest(OAuthCredentials):
    """Request body for manual credential submission."""


class TokenCache(BaseModel):
    """In-memory representation of an issued OAuth2 token."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    scope: Optional[str] = None
    raw_response: dict[str, Any]


class TokenResponse(BaseModel):
    """Response envelope for access token retrieval."""

    access_token: str = Field(..., description="Access token string from OAuth2 provider.")
    token_type: str = Field("bearer", description="Token type as reported by OAuth2 provider.")
    expires_at: datetime = Field(..., description="UTC timestamp when the token expires.")
    scope: Optional[str] = Field(None, description="Scopes granted to the token.")


class TokenHealth(BaseModel):
    """Health payload describing the current token state."""

    token_present: bool
    expires_at: Optional[datetime]
    expires_in_seconds: Optional[int]
    expires_soon: bool


class TokenDecodeRequest(BaseModel):
    """Request body for decoding JWTs without validation."""

    token: str
