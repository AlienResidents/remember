---
type: Source Code
description: "Tests for web UI auth — C3 (userinfo failure) and H2 (OAuth state)."
resource: server/tests/test_web_auth.py
timestamp: 2026-07-10T02:44:34Z
---

# test web auth

Source path: `server/tests/test_web_auth.py`

## Content

```python
"""Tests for web UI auth — C3 (userinfo failure) and H2 (OAuth state)."""

import uuid

import pytest

from remember.web import _get_or_create_user


# ---------------------------------------------------------------------------
# C3: _get_or_create_user must NOT fall back to a default UUID
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_or_create_user_raises_on_missing_sub():
    """C3: If Keycloak userinfo is missing 'sub', raise — don't return default UUID."""
    with pytest.raises(ValueError, match="missing 'sub'"):
        await _get_or_create_user({})


@pytest.mark.asyncio
async def test_get_or_create_user_raises_on_empty_userinfo():
    """C3: Empty userinfo dict must raise, not silently return default UUID."""
    with pytest.raises(ValueError, match="missing 'sub'"):
        await _get_or_create_user(None)


@pytest.mark.asyncio
async def test_get_or_create_user_raises_on_none():
    """C3: None userinfo must raise."""
    with pytest.raises(ValueError, match="missing 'sub'"):
        await _get_or_create_user(None)


@pytest.mark.asyncio
async def test_get_or_create_user_does_not_return_default_uuid():
    """C3: The hardcoded default UUID 00000000-...-000000000001 must never be returned."""
    # Test all the failure conditions that used to return the default UUID.
    # These all raise ValueError before touching the database.
    for bad_input in [{}, None, {"foo": "bar"}]:
```

*…truncated — full source at `server/tests/test_web_auth.py`*
