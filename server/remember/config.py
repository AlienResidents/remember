"""Configuration settings."""

from pydantic import Field
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
    client_user_mapping: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Map Keycloak client ID (azp claim) to username for fallback "
            "identity resolution. Used when a tool caller doesn't provide "
            "explicit owner_id/user_id. e.g. {\"remember-pi\": \"chrispy\"}"
        ),
    )

    @property
    def keycloak_enabled(self) -> bool:
        """Whether Keycloak JWT validation is active."""
        return bool(self.keycloak_authority) and not self.dev_mode

    @property
    def keycloak_jwks_url(self) -> str:
        """Keycloak JWKS endpoint for fetching public keys."""
        if not self.keycloak_authority:
            return ""
        return f"{self.keycloak_authority}/realms/{self.keycloak_realm}/protocol/openid-connect/certs"

    @property
    def keycloak_issuer(self) -> str:
        """Expected JWT issuer claim."""
        if not self.keycloak_authority:
            return ""
        return f"{self.keycloak_authority}/realms/{self.keycloak_realm}"


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
