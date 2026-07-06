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
            else:
                provider_id = "dev-user"

            stmt = select(User).where(User.provider == "dev", User.provider_id == provider_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                # Create dev user
                user = User(
                    id=uuid.uuid4() if not self.config.default_user_id else uuid.UUID(self.config.default_user_id),
                    provider="dev",
                    provider_id=provider_id,
                    display_name="Dev User",
                    email="dev@localhost",
                    created_at=datetime.now(timezone.utc),
                    last_seen_at=datetime.now(timezone.utc),
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

            return AuthResult(
                user_id=user.id,
                provider="dev",
                provider_id=user.provider_id,
                display_name=user.display_name,
                email=user.email,
            )

    def get_callback_url(self) -> str:
        """Dev auth doesn't have a callback URL."""
        return ""
