---
type: Source Code
description: "Keycloak OAuth authentication provider."
resource: server/remember/auth/keycloak.py
timestamp: 2026-07-09T14:09:53Z
---

# keycloak

Source path: `server/remember/auth/keycloak.py`

## Content

```python
"""Keycloak OAuth authentication provider."""

import uuid
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class KeycloakConfig(BaseModel):
    """Keycloak configuration."""

    enabled: bool = Field(default=False, description="Enable Keycloak auth")
    authority: str = Field(default="", description="Keycloak server URL (e.g., https://keycloak.example.com)")
    realm: str = Field(default="master", description="Keycloak realm")
    client_id: str = Field(default="", description="OAuth client ID")
    client_secret: str = Field(default="", description="OAuth client secret")
    redirect_uri: str = Field(default="http://localhost:8000/auth/callback", description="OAuth callback URL")

    @property
    def authority_url(self) -> str:
        """Get the Keycloak authority URL."""
        return f"{self.authority}/realms/{self.realm}"


class KeycloakAuthProvider(AuthProvider):
    """Keycloak OAuth authentication provider."""

    def __init__(self, config: KeycloakConfig):
        self.config = config

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via Keycloak OAuth.

        Args:
            code: OAuth authorization code
```

*…truncated — full source at `server/remember/auth/keycloak.py`*
