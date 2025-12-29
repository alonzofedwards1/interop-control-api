"""Application configuration using environment-driven settings."""
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment driven configuration for the Interop Control API."""

    service_name: str = Field("interop-control-api", description="Service identifier exposed by health endpoints.")
    environment: str = Field("local", description="Deployment environment label.")

    oauth_token_url: str | None = Field(
        default=None, description="OAuth2 token endpoint for external systems (e.g., OpenEMR)."
    )
    oauth_client_id: str | None = Field(default=None, description="OAuth2 client identifier for password grant.")
    oauth_client_secret: str | None = Field(default=None, description="OAuth2 client secret for password grant.")
    oauth_username: str | None = Field(default=None, description="Resource owner username for password grant.")
    oauth_password: str | None = Field(default=None, description="Resource owner password for password grant.")
    oauth_scope: str | None = Field(
        default=None, description="Optional space-delimited scopes to request from the OAuth2 provider."
    )
    expires_soon_seconds: int = Field(
        default=120,
        ge=30,
        description="Threshold (seconds) used to proactively refresh tokens before they expire.",
    )

    pd_endpoint_url: str | None = Field(default=None, description="Configured Mirth/OpenEMR endpoint for patient discovery triggers.")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    """Return cached settings instance to avoid re-parsing environment variables."""
    # Pydantic caches settings automatically when using lru_cache is unnecessary in v2.
    return Settings()
