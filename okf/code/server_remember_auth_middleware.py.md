---
type: Source Code
description: "Authentication middleware."
resource: server/remember/auth/middleware.py
timestamp: 2026-07-09T14:09:53Z
---

# middleware

Source path: `server/remember/auth/middleware.py`

## Content

```python
"""Authentication middleware."""

import uuid
from typing import Callable

from fastmcp import Context
from pydantic import BaseModel

from remember.auth import (
    AuthProvider,
    AuthResult,
    GitHubAuthProvider,
    APIKeyAuthProvider,
    DevAuthProvider,
    TailscaleAuthProvider,
    GoogleAuthProvider,
    MicrosoftAuthProvider,
    KeycloakAuthProvider,
    AuthentikAuthProvider,
    DexAuthProvider,
)
from remember.auth.github import GitHubOAuthConfig
from remember.auth.api_key import APIKeyConfig
from remember.auth.dev import DevAuthConfig
from remember.auth.tailscale import TailscaleAuthConfig
from remember.auth.google import GoogleOAuthConfig
from remember.auth.microsoft import MicrosoftOAuthConfig
from remember.auth.keycloak import KeycloakConfig
from remember.auth.authentik import AuthentikConfig
from remember.auth.dex import DexConfig


class AuthMiddleware:
    """Authentication middleware for MCP tools."""

    def __init__(self, providers: list[AuthProvider]):
        self.providers = {p.__class__.__name__: p for p in providers}

    async def authenticate(self, ctx: Context, **kwargs) -> AuthResult:
        """Authenticate the current request.
```

*…truncated — full source at `server/remember/auth/middleware.py`*
