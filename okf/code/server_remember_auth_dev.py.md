---
type: Source Code
description: "Development authentication provider (skip auth)."
resource: server/remember/auth/dev.py
timestamp: 2026-07-10T02:44:33Z
---

# dev

Source path: `server/remember/auth/dev.py`

## Content

```python
"""Development authentication provider (skip auth)."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class DevAuthConfig(BaseModel):
    """Dev auth configuration."""

    enabled: bool = Field(default=False, description="Enable dev auth (skip authentication)")
    default_user_id: str | None = Field(default=None, description="Force a specific user ID for testing")


class DevAuthProvider(AuthProvider):
    """Development authentication provider (skip auth)."""

    def __init__(self, config: DevAuthConfig):
        self.config = config

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate in dev mode (always succeeds).

        Args:
            **kwargs: Ignored in dev mode

        Returns:
            AuthResult with dev user information
        """
        async with async_session_factory() as db:
            from sqlalchemy import select

            # Use forced user ID if provided
            if self.config.default_user_id:
                provider_id = self.config.default_user_id
```

*…truncated — full source at `server/remember/auth/dev.py`*
