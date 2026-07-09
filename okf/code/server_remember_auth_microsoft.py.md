---
type: Source Code
description: "Microsoft/Entra ID OAuth authentication provider."
resource: server/remember/auth/microsoft.py
timestamp: 2026-07-09T01:43:39Z
---

# microsoft

Source path: `server/remember/auth/microsoft.py`

## Content

```python
"""Microsoft/Entra ID OAuth authentication provider."""

import uuid
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class MicrosoftOAuthConfig(BaseModel):
    """Microsoft OAuth configuration."""

    client_id: str = Field(..., description="Microsoft OAuth client ID")
    client_secret: str = Field(..., description="Microsoft OAuth client secret")
    tenant_id: str = Field(default="common", description="Azure AD tenant ID")
    redirect_uri: str = Field(default="http://localhost:8000/auth/callback", description="OAuth callback URL")


class MicrosoftAuthProvider(AuthProvider):
    """Microsoft/Entra ID OAuth authentication provider."""

    def __init__(self, config: MicrosoftOAuthConfig):
        self.config = config
        self._base_url = f"https://login.microsoftonline.com/{config.tenant_id}"
        self._api_url = "https://graph.microsoft.com"

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via Microsoft OAuth.

        Args:
            code: OAuth authorization code
            state: OAuth state parameter

        Returns:
            AuthResult with Microsoft user information

```

*…truncated — full source at `server/remember/auth/microsoft.py`*
