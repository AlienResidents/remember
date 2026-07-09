---
type: Source Code
description: "Google OAuth authentication provider."
resource: server/remember/auth/google.py
timestamp: 2026-07-09T13:05:53Z
---

# google

Source path: `server/remember/auth/google.py`

## Content

```python
"""Google OAuth authentication provider."""

import uuid
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class GoogleOAuthConfig(BaseModel):
    """Google OAuth configuration."""

    client_id: str = Field(..., description="Google OAuth client ID")
    client_secret: str = Field(..., description="Google OAuth client secret")
    redirect_uri: str = Field(default="http://localhost:8000/auth/callback", description="OAuth callback URL")


class GoogleAuthProvider(AuthProvider):
    """Google OAuth authentication provider."""

    def __init__(self, config: GoogleOAuthConfig):
        self.config = config
        self._base_url = "https://accounts.google.com"
        self._api_url = "https://www.googleapis.com"

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via Google OAuth.

        Args:
            code: OAuth authorization code
            state: OAuth state parameter

        Returns:
            AuthResult with Google user information

        Raises:
```

*…truncated — full source at `server/remember/auth/google.py`*
