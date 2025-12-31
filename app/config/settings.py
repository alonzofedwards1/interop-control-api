from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- Core ----
    service_name: str = "interop-control-api"
    environment: str = "local"
    auth_mode: str = "system"

    # ---- SYSTEM OAuth (Phase 1) ----
    oauth_token_url: str | None = None
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = None
    oauth_username: str | None = None
    oauth_password: str | None = None
    oauth_scope: str | None = None

    # ---- SMART OAuth (Phase 2 – dormant) ----
    smart_client_id: str | None = None
    smart_client_secret: str | None = None
    smart_aud: str | None = None

    expires_soon_seconds: int = Field(
        default=120,
        ge=30,
    )

    # Patient Discovery downstream endpoint
    pd_endpoint_url: str | None = Field(default=None)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
