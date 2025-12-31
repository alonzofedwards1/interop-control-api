from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class OAuthCredentials(BaseModel):
    token_url: str
    client_id: str
    client_secret: str
    username: str
    password: str
    scope: Optional[str] = None


class ManualTokenRequest(OAuthCredentials):
    pass


class TokenCache(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    scope: Optional[str] = None
    raw_response: dict[str, Any]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    scope: Optional[str] = None


class TokenHealth(BaseModel):
    token_present: bool
    expires_at: Optional[datetime]
    expires_in_seconds: Optional[int]
    expires_soon: bool


class TokenDecodeRequest(BaseModel):
    token: str
