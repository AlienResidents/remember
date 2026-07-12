"""Configuration settings."""

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = Field(
        default="postgresql+asyncpg://localhost:5432/remember",
        description="Database URL",
    )
    echo: bool = Field(default=False, description="Enable SQL logging")
    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=20, description="Max overflow connections")

    @property
    def async_url(self) -> str:
        """Return async database URL."""
        return self.url.replace("postgresql://", "postgresql+asyncpg://")


class ServerSettings(BaseSettings):
    """Server configuration."""

    host: str = Field(default="0.0.0.0", description="Bind address")
    port: int = Field(default=8000, description="Bind port")
    workers: int = Field(default=2, description="Number of workers")
    log_level: str = Field(
        default="INFO",
        description="Root logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )


class AuthSettings(BaseSettings):
    """Authentication configuration."""

    providers: list[dict] = Field(
        default_factory=list,
        description="List of auth provider configs",
    )
    dev_mode: bool = Field(
        default=False,
        description="Skip auth for development",
    )
    keycloak_authority: str = Field(
        default="",
        description="Keycloak server URL for JWT validation (e.g. https://keycloak.example.com)",
    )
    keycloak_realm: str = Field(
        default="master",
        description="Keycloak realm for JWT validation",
    )
    keycloak_client_id: str = Field(
        default="",
        description="Expected client ID (azp claim) — tokens from other clients are rejected",
    )
    keycloak_client_secret: str = Field(
        default="",
        description="Keycloak client secret for authorization_code flow (web UI)",
    )
    session_secret: str = Field(
        default="",
        description="Secret key for signing session cookies (web UI only)",
    )
    keycloak_jwks_url: str = Field(
        default="",
        description="JWKS endpoint. If empty, derived from keycloak_authority. "
        "Set to an in-cluster service URL to bypass ingress for JWKS fetches.",
    )
    keycloak_issuer: str = Field(
        default="",
        description="Expected JWT iss claim. If empty, derived from keycloak_authority. "
        "Must match the issuer that signed the tokens (typically the external URL).",
    )

    @model_validator(mode="after")
    def _derive_keycloak_urls(self) -> "AuthSettings":
        """Derive keycloak_jwks_url and keycloak_issuer from authority if not set."""
        if self.keycloak_authority:
            base = f"{self.keycloak_authority}/realms/{self.keycloak_realm}"
            if not self.keycloak_issuer:
                self.keycloak_issuer = base
            if not self.keycloak_jwks_url:
                self.keycloak_jwks_url = (
                    f"{base}/protocol/openid-connect/certs"
                )
        return self

    @property
    def keycloak_enabled(self) -> bool:
        """Whether Keycloak JWT validation is active."""
        return bool(self.keycloak_authority) and not self.dev_mode


class SearchSettings(BaseSettings):
    """Search configuration."""

    type: str = Field(default="fulltext", description="Search type: fulltext or hybrid")
    default_limit: int = Field(default=10, description="Default search limit")


class StalenessSettings(BaseSettings):
    """Staleness detection configuration."""

    threshold_days: int = Field(default=90, description="Days before marking as stale")


class Settings(BaseSettings):
    """Application settings."""

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    staleness: StalenessSettings = Field(default_factory=StalenessSettings)

    model_config = {"env_prefix": "REMEMBER_", "env_nested_delimiter": "__", "env_file": ".env"}


settings = Settings()
