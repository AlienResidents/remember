---
type: Source Code
description: "Configuration settings."
resource: server/remember/config.py
timestamp: 2026-07-09T13:05:53Z
---

# config

Source path: `server/remember/config.py`

## Content

```python
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
```

*…truncated — full source at `server/remember/config.py`*
