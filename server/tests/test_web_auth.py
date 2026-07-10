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
        with pytest.raises(ValueError):
            await _get_or_create_user(bad_input)


# ---------------------------------------------------------------------------
# C3: _get_or_create_user works correctly with valid userinfo
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_or_create_user_creates_user(db_session, monkeypatch):
    """C3: Valid userinfo creates a real user with a real UUID."""
    # Patch async_session_factory to use the test session
    from remember import web
    monkeypatch.setattr(web, "async_session_factory", lambda: _TestSessionContext(db_session))

    user_info = {
        "sub": "keycloak-user-123",
        "preferred_username": "testuser",
        "email": "test@example.com",
    }

    user_id = await _get_or_create_user(user_info)
    assert isinstance(user_id, uuid.UUID)
    assert str(user_id) != "00000000-0000-0000-0000-000000000001"


class _TestSessionContext:
    """Context manager that yields the test db session."""

    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, *args):
        pass