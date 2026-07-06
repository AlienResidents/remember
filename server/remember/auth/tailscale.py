"""Tailscale identity authentication provider."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class TailscaleAuthConfig(BaseModel):
    """Tailscale authentication configuration."""

    enabled: bool = Field(default=False, description="Enable Tailscale auth")
    tailnet: str = Field(default="", description="Tailnet name (e.g., 'myteam.ts.net')")


class TailscaleAuthProvider(AuthProvider):
    """Tailscale identity authentication provider.

    Authenticates users via Tailscale identity headers forwarded by the Tailscale Kubernetes operator.
    """

    def __init__(self, config: TailscaleAuthConfig):
        self.config = config

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via Tailscale identity.

        Args:
            tailnet_user: Tailscale user login (e.g., 'user@myteam.ts.net')
            tailnet_name: Tailscale name (optional)

        Returns:
            AuthResult with Tailscale user information

        Raises:
            AuthenticationError: If Tailscale identity is missing or invalid
        """
        tailnet_user = kwargs.get("tailnet_user")
        if not tailnet_user:
            raise AuthenticationError("Missing Tailscale user identity")

        # Parse tailnet user (format: user@tailnet.ts.net)
        if "@" not in tailnet_user:
            raise AuthenticationError("Invalid Tailscale user format (expected user@tailnet.ts.net)")

        # Get or create user in database
        async with async_session_factory() as db:
            from sqlalchemy import select

            stmt = select(User).where(User.provider == "tailscale", User.provider_id == tailnet_user)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                # Extract display name from tailnet user
                display_name = tailnet_user.split("@")[0]
                if self.config.tailnet:
                    display_name = f"{display_name} ({self.config.tailnet})"

                user = User(
                    id=uuid.uuid4(),
                    provider="tailscale",
                    provider_id=tailnet_user,
                    display_name=display_name,
                    email=tailnet_user,
                    created_at=datetime.now(timezone.utc),
                    last_seen_at=datetime.now(timezone.utc),
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

            return AuthResult(
                user_id=user.id,
                provider="tailscale",
                provider_id=user.provider_id,
                display_name=user.display_name,
                email=user.email,
            )

    def get_callback_url(self) -> str:
        """Tailscale auth doesn't have a callback URL."""
        return ""


class AuthenticationError(Exception):
    """Authentication failed."""

    pass
