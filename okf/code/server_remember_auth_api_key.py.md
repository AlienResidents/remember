---
type: Source Code
description: "API key authentication provider."
resource: server/remember/auth/api_key.py
timestamp: 2026-07-09T14:09:53Z
---

# api key

Source path: `server/remember/auth/api_key.py`

## Content

```python
"""API key authentication provider."""

import uuid
import secrets
from datetime import datetime, timezone

import bcrypt

from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class APIKeyConfig(BaseModel):
    """API key configuration."""

    enabled: bool = Field(default=True, description="Enable API key auth")
    header_name: str = Field(default="X-API-Key", description="Header name for API key")


class APIKeyAuthProvider(AuthProvider):
    """API key authentication provider."""

    def __init__(self, config: APIKeyConfig):
        self.config = config

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via API key.

        Args:
            api_key: API key from kwargs or headers

        Returns:
            AuthResult with user information

        Raises:
            AuthenticationError: If API key is invalid
        """
```

*…truncated — full source at `server/remember/auth/api_key.py`*
