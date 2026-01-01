from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- Core ----
    service_name: str = "interop-control-api"
    environment: str = "local"
    auth_mode: str = "system"

    # ---- OAuth (Phase 1 – owned by FastAPI, not Mirth) ----
    oauth_token_url: str | None = None
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = None
    oauth_username: str | None = None
    oauth_password: str | None = None
    oauth_scope: str | None = None

    expires_soon_seconds: int = Field(default=120, ge=30)

    # ---- Patient Discovery ----
    pd_endpoint_url: str = Field(
        default="http://100.27.251.103:6662/pd/trigger/",
        validation_alias="PD_ENDPOINT_URL",
    )
    pd_storage_dir: str = "./data/pd"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
