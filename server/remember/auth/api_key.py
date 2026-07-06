"""API key authentication provider."""

import uuid
import hashlib
import secrets
from datetime import datetime, timezone

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
        api_key = kwargs.get("api_key")
        if not api_key:
            raise AuthenticationError("Missing API key")

        # Hash the API key for storage
        key_hash = self._hash_key(api_key)

        # Look up user by API key hash
        async with async_session_factory() as db:
            from sqlalchemy import select
            stmt = select(User).where(User.provider == "api_key", User.provider_id == key_hash)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise AuthenticationError("Invalid API key")

            # Update last seen
            user.last_seen_at = datetime.now(timezone.utc)
            await db.commit()

            return AuthResult(
                user_id=user.id,
                provider="api_key",
                provider_id=user.provider_id,
                display_name=user.display_name,
                email=user.email,
            )

    def get_callback_url(self) -> str:
        """API keys don't have a callback URL."""
        return ""

    def generate_api_key(self) -> str:
        """Generate a new API key.

        Returns:
            Raw API key (only shown once)
        """
        return secrets.token_urlsafe(32)

    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage.

        Args:
            api_key: Raw API key

        Returns:
            SHA-256 hash of the API key
        """
        return self._hash_key(api_key)

    def _hash_key(self, key: str) -> str:
        """Hash an API key."""
        return hashlib.sha256(key.encode()).hexdigest()


class AuthenticationError(Exception):
    """Authentication failed."""

    pass
