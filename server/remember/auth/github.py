"""GitHub OAuth authentication provider."""

import uuid
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, Field

from remember.auth.base import AuthProvider, AuthResult
from remember.db import async_session_factory
from remember.models import User


class GitHubOAuthConfig(BaseModel):
    """GitHub OAuth configuration."""

    client_id: str = Field(..., description="GitHub OAuth client ID")
    client_secret: str = Field(..., description="GitHub OAuth client secret")
    redirect_uri: str = Field(default="http://localhost:8000/auth/callback", description="OAuth callback URL")


class GitHubAuthProvider(AuthProvider):
    """GitHub OAuth authentication provider."""

    def __init__(self, config: GitHubOAuthConfig):
        self.config = config
        self._base_url = "https://github.com"
        self._api_url = "https://api.github.com"

    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate via GitHub OAuth.

        Args:
            code: OAuth authorization code
            state: OAuth state parameter

        Returns:
            AuthResult with GitHub user information

        Raises:
            AuthenticationError: If authentication fails
        """
        code = kwargs.get("code")
        if not code:
            raise AuthenticationError("Missing authorization code")

        # Exchange code for access token
        token_response = await self._exchange_code(code)
        access_token = token_response["access_token"]

        # Get user info
        user_info = await self._get_user_info(access_token)

        # Get or create user in database
        async with async_session_factory() as db:
            user = await self._get_or_create_user(db, user_info)
            await db.commit()

            return AuthResult(
                user_id=user.id,
                provider="github",
                provider_id=user.provider_id,
                display_name=user.display_name,
                email=user.email,
            )

    def get_callback_url(self) -> str:
        """Get the OAuth callback URL."""
        return self.config.redirect_uri

    async def _exchange_code(self, code: str) -> dict:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/login/oauth/access_token",
                json={
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "code": code,
                    "redirect_uri": self.config.redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _get_user_info(self, access_token: str) -> dict:
        """Get GitHub user info."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._api_url}/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            response.raise_for_status()
            return response.json()

    async def _get_or_create_user(self, db, user_info: dict) -> User:
        """Get or create a user from GitHub info."""
        from sqlalchemy import select

        provider_id = str(user_info["id"])
        stmt = select(User).where(User.provider == "github", User.provider_id == provider_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Update last seen
            user.last_seen_at = datetime.now(timezone.utc)
            return user

        # Create new user
        user = User(
            id=uuid.uuid4(),
            provider="github",
            provider_id=provider_id,
            display_name=user_info.get("name", user_info.get("login", "Unknown")),
            email=user_info.get("email"),
            created_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
        )
        db.add(user)
        return user


class AuthenticationError(Exception):
    """Authentication failed."""

    pass
