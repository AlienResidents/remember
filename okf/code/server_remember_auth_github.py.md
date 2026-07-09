---
type: Source Code
description: "GitHub OAuth authentication provider."
resource: server/remember/auth/github.py
timestamp: 2026-07-09T14:09:53Z
---

# github

Source path: `server/remember/auth/github.py`

## Content

```python
"""GitHub OAuth authentication provider."""

import uuid
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class GitHubOAuthConfig(BaseModel):
    """GitHub OAuth configuration."""

    client_id: str = Field(..., description="GitHub OAuth client ID")
    client_secret: str = Field(..., description="GitHub OAuth client secret")
    redirect_uri: str = Field(default="http://localhost:8000/auth/callback", description="OAuth callback URL")


class GitHubAuthProvider(AuthProvider):
    """GitHub OAuth authentication provider."""

    def __init__(self, config: GitHubOAuthConfig):
        self.config = config
        self._base_url = "https://github.com"
        self._api_url = "https://api.github.com"

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via GitHub OAuth.

        Args:
            code: OAuth authorization code
            state: OAuth state parameter

        Returns:
            AuthResult with GitHub user information

        Raises:
```

*…truncated — full source at `server/remember/auth/github.py`*
