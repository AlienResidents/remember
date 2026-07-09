---
type: Source Code
description: "Tests for authentication providers."
resource: server/tests/test_auth.py
timestamp: 2026-07-09T01:43:40Z
---

# test auth

Source path: `server/tests/test_auth.py`

## Content

```python
"""Tests for authentication providers."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from remember.auth import DevAuthProvider, APIKeyAuthProvider
from remember.auth.dev import DevAuthConfig
from remember.auth.api_key import APIKeyConfig
from remember.auth.base import AuthResult


@pytest.mark.asyncio
async def test_dev_auth_provides_user(db_session: AsyncSession):
    """Test dev auth provides a user."""
    config = DevAuthConfig(enabled=True)
    provider = DevAuthProvider(config)

    result = await provider.authenticate()

    assert isinstance(result, AuthResult)
    assert result.provider == "dev"
    assert result.user_id is not None
    assert result.display_name == "Dev User"


@pytest.mark.asyncio
async def test_dev_auth_idempotent(db_session: AsyncSession):
    """Test dev auth is idempotent (same user on multiple calls)."""
    config = DevAuthConfig(enabled=True)
    provider = DevAuthProvider(config)

    result1 = await provider.authenticate()
    result2 = await provider.authenticate()

    assert result1.user_id == result2.user_id


```

*…truncated — full source at `server/tests/test_auth.py`*
