---
type: Source Code
description: "Tailscale identity authentication provider."
resource: server/remember/auth/tailscale.py
timestamp: 2026-07-09T01:43:39Z
---

# tailscale

Source path: `server/remember/auth/tailscale.py`

## Content

```python
"""Tailscale identity authentication provider."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class TailscaleAuthConfig(BaseModel):
    """Tailscale authentication configuration."""

    enabled: bool = Field(default=False, description="Enable Tailscale auth")
    tailnet: str = Field(default="", description="Tailnet name (e.g., 'myteam.ts.net')")


class TailscaleAuthProvider(AuthProvider):
    """Tailscale identity authentication provider.

    Authenticates users via Tailscale identity headers forwarded by the Tailscale Kubernetes operator.
    """

    def __init__(self, config: TailscaleAuthConfig):
        self.config = config

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via Tailscale identity.

        Args:
            tailnet_user: Tailscale user login (e.g., 'user@myteam.ts.net')
            tailnet_name: Tailscale name (optional)

        Returns:
            AuthResult with Tailscale user information

        Raises:
            AuthenticationError: If Tailscale identity is missing or invalid
```

*…truncated — full source at `server/remember/auth/tailscale.py`*
