---
type: Source Code
description: "Tests for extended authentication providers."
resource: server/tests/test_auth_extended.py
timestamp: 2026-07-09T13:05:54Z
---

# test auth extended

Source path: `server/tests/test_auth_extended.py`

## Content

```python
"""Tests for extended authentication providers."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from remember.auth import TailscaleAuthProvider, GoogleAuthProvider, MicrosoftAuthProvider
from remember.auth.tailscale import TailscaleAuthConfig, AuthenticationError as TailscaleAuthError
from remember.auth.google import GoogleOAuthConfig
from remember.auth.microsoft import MicrosoftOAuthConfig
from remember.auth.base import AuthResult


@pytest.mark.asyncio
async def test_tailscale_auth_provides_user(db_session: AsyncSession):
    """Test tailscale auth provides a user."""
    config = TailscaleAuthConfig(enabled=True, tailnet="test.ts.net")
    provider = TailscaleAuthProvider(config)

    result = await provider.authenticate(tailnet_user="user@test.ts.net")

    assert isinstance(result, AuthResult)
    assert result.provider == "tailscale"
    assert result.provider_id == "user@test.ts.net"
    assert result.display_name == "user (test.ts.net)"


@pytest.mark.asyncio
async def test_tailscale_auth_idempotent(db_session: AsyncSession):
    """Test tailscale auth is idempotent."""
    config = TailscaleAuthConfig(enabled=True, tailnet="test.ts.net")
    provider = TailscaleAuthProvider(config)

    result1 = await provider.authenticate(tailnet_user="user@test.ts.net")
    result2 = await provider.authenticate(tailnet_user="user@test.ts.net")

    assert result1.user_id == result2.user_id

```

*…truncated — full source at `server/tests/test_auth_extended.py`*
