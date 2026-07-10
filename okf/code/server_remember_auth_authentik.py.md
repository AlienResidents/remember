---
type: Source Code
description: "Authentik OAuth authentication provider."
resource: server/remember/auth/authentik.py
timestamp: 2026-07-10T02:44:33Z
---

# authentik

Source path: `server/remember/auth/authentik.py`

## Content

```python
"""Authentik OAuth authentication provider."""

import uuid
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class AuthentikConfig(BaseModel):
    """Authentik configuration."""

    enabled: bool = Field(default=False, description="Enable Authentik auth")
    authority: str = Field(default="", description="Authentik server URL (e.g., https://authentik.example.com)")
    client_id: str = Field(default="", description="OAuth client ID")
    client_secret: str = Field(default="", description="OAuth client secret")
    redirect_uri: str = Field(default="http://localhost:8000/auth/callback", description="OAuth callback URL")


class AuthentikAuthProvider(AuthProvider):
    """Authentik OAuth authentication provider."""

    def __init__(self, config: AuthentikConfig):
        self.config = config

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via Authentik OAuth.

        Args:
            code: OAuth authorization code

        Returns:
            AuthResult with Authentik user information

        Raises:
            AuthenticationError: If authentication fails
```

*…truncated — full source at `server/remember/auth/authentik.py`*
