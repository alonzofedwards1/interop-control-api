import logging

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- Core ----
    service_name: str = "interop-control-api"
    environment: str = "local"
    auth_mode: str = "system"

    # ---- Control Plane ----
    control_plane_base_url: str = Field(
        default="http://100.27.251.103:8000",
        validation_alias="CONTROL_PLANE_BASE_URL",
    )

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
    pd_callback_url: str | None = Field(
        default=None,
        validation_alias="PD_CALLBACK_URL",
    )
    pd_storage_dir: str = "./data/pd"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def model_post_init(self, __context):
        # Normalize base URL and warn on localhost usage outside local envs.
        normalized_base = self.control_plane_base_url.rstrip("/")
        if normalized_base != self.control_plane_base_url:
            self.control_plane_base_url = normalized_base

        if self.environment != "local" and "localhost" in self.control_plane_base_url:
            logging.warning(
                "CONTROL_PLANE_BASE_URL points to localhost while environment=%s", self.environment
            )

        logging.info("CONTROL_PLANE_BASE_URL resolved to %s", self.control_plane_base_url)

        # Default the PD callback to the control plane base URL when not provided.
        if not self.pd_callback_url:
            self.pd_callback_url = f"{self.control_plane_base_url}/api/pd/callback"


def get_settings() -> Settings:
    return Settings()
