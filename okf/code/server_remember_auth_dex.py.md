---
type: Source Code
description: "Dex OAuth authentication provider."
resource: server/remember/auth/dex.py
timestamp: 2026-07-09T01:43:39Z
---

# dex

Source path: `server/remember/auth/dex.py`

## Content

```python
"""Dex OAuth authentication provider."""

import uuid
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class DexConfig(BaseModel):
    """Dex configuration."""

    enabled: bool = Field(default=False, description="Enable Dex auth")
    authority: str = Field(default="", description="Dex server URL (e.g., https://dex.example.com)")
    client_id: str = Field(default="", description="OAuth client ID")
    client_secret: str = Field(default="", description="OAuth client secret")
    redirect_uri: str = Field(default="http://localhost:8000/auth/callback", description="OAuth callback URL")


class DexAuthProvider(AuthProvider):
    """Dex OAuth authentication provider."""

    def __init__(self, config: DexConfig):
        self.config = config

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via Dex OAuth.

        Args:
            code: OAuth authorization code

        Returns:
            AuthResult with Dex user information

        Raises:
            AuthenticationError: If authentication fails
```

*…truncated — full source at `server/remember/auth/dex.py`*
