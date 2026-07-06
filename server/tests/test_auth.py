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


@pytest.mark.asyncio
async def test_dev_auth_with_forced_user_id(db_session: AsyncSession):
    """Test dev auth with forced user ID."""
    forced_id = str(uuid.uuid4())
    config = DevAuthConfig(enabled=True, default_user_id=forced_id)
    provider = DevAuthProvider(config)

    result = await provider.authenticate()

    assert str(result.user_id) == forced_id


@pytest.mark.asyncio
async def test_api_key_auth_invalid_key(db_session: AsyncSession):
    """Test API key auth with invalid key."""
    config = APIKeyConfig(enabled=True)
    provider = APIKeyAuthProvider(config)

    with pytest.raises(Exception):  # Should raise AuthenticationError
        await provider.authenticate(api_key="invalid-key")


@pytest.mark.asyncio
async def test_api_key_auth_valid_key(db_session: AsyncSession):
    """Test API key auth with valid key."""
    from remember.models import User
    from remember.auth.api_key import APIKeyAuthProvider

    # Create a user with API key
    import hashlib
    test_key = "test-api-key-123"
    key_hash = hashlib.sha256(test_key.encode()).hexdigest()

    user = User(
        id=uuid.uuid4(),
        provider="api_key",
        provider_id=key_hash,
        display_name="API Key User",
        email="api@example.com",
    )
    db_session.add(user)
    await db_session.commit()

    provider = APIKeyAuthProvider(APIKeyConfig(enabled=True))
    result = await provider.authenticate(api_key=test_key)

    assert isinstance(result, AuthResult)
    assert result.provider == "api_key"
    assert result.display_name == "API Key User"


@pytest.mark.asyncio
async def test_api_key_generate_and_validate():
    """Test API key generation and validation."""
    provider = APIKeyAuthProvider(APIKeyConfig(enabled=True))

    # Generate key
    key = provider.generate_api_key()
    assert len(key) > 0

    # Hash it
    hashed = provider.hash_api_key(key)
    assert len(hashed) == 64  # SHA-256 hex digest

    # Verify hash is consistent
    hashed2 = provider.hash_api_key(key)
    assert hashed == hashed2


@pytest.mark.asyncio
async def test_auth_middleware_from_config():
    """Test AuthMiddleware from config."""
    from remember.auth.middleware import AuthMiddleware

    config = {
        "dev": {"enabled": True},
        "api_key": {"enabled": True},
    }

    middleware = AuthMiddleware.from_config(config)

    assert len(middleware.providers) == 2
    assert "DevAuthProvider" in middleware.providers
    assert "APIKeyAuthProvider" in middleware.providers
