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


@pytest.mark.asyncio
async def test_tailscale_auth_invalid_format(db_session: AsyncSession):
    """Test tailscale auth with invalid format."""
    config = TailscaleAuthConfig(enabled=True)
    provider = TailscaleAuthProvider(config)

    with pytest.raises(TailscaleAuthError):
        await provider.authenticate(tailnet_user="invalid-user")


@pytest.mark.asyncio
async def test_google_auth_missing_code(db_session: AsyncSession):
    """Test Google auth with missing code."""
    config = GoogleOAuthConfig(client_id="test", client_secret="test")
    provider = GoogleAuthProvider(config)

    with pytest.raises(Exception):  # Should raise AuthenticationError
        await provider.authenticate()


@pytest.mark.asyncio
async def test_microsoft_auth_missing_code(db_session: AsyncSession):
    """Test Microsoft auth with missing code."""
    config = MicrosoftOAuthConfig(client_id="test", client_secret="test")
    provider = MicrosoftAuthProvider(config)

    with pytest.raises(Exception):  # Should raise AuthenticationError
        await provider.authenticate()


@pytest.mark.asyncio
async def test_auth_middleware_extended_providers():
    """Test AuthMiddleware with extended providers."""
    from remember.auth.middleware import AuthMiddleware

    config = {
        "tailscale": {"enabled": True, "tailnet": "test.ts.net"},
        "google": {"client_id": "test", "client_secret": "test"},
        "microsoft": {"client_id": "test", "client_secret": "test", "tenant_id": "common"},
    }

    middleware = AuthMiddleware.from_config(config)

    assert len(middleware.providers) == 3
    assert "TailscaleAuthProvider" in middleware.providers
    assert "GoogleAuthProvider" in middleware.providers
    assert "MicrosoftAuthProvider" in middleware.providers
