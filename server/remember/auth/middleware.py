"""Authentication middleware."""

import uuid
from typing import Callable

from fastmcp import Context
from pydantic import BaseModel

from remember.auth import AuthProvider, AuthResult, GitHubAuthProvider, APIKeyAuthProvider, DevAuthProvider
from remember.auth.github import GitHubOAuthConfig, AuthenticationError as GitHubAuthError
from remember.auth.api_key import APIKeyConfig, AuthenticationError as APIKeyAuthError
from remember.auth.dev import DevAuthConfig


class AuthMiddleware:
    """Authentication middleware for MCP tools."""

    def __init__(self, providers: list[AuthProvider]):
        self.providers = {p.__class__.__name__: p for p in providers}

    async def authenticate(self, ctx: Context, **kwargs) -> AuthResult:
        """Authenticate the current request.

        Args:
            ctx: MCP context
            **kwargs: Authentication credentials

        Returns:
            AuthResult with user information

        Raises:
            AuthenticationError: If authentication fails
        """
        # Try each provider in order
        for provider in self.providers.values():
            try:
                result = await provider.authenticate(**kwargs)
                return result
            except Exception:
                continue

        raise AuthenticationError("No valid authentication method found")

    @classmethod
    def from_config(cls, config: dict) -> "AuthMiddleware":
        """Create AuthMiddleware from configuration.

        Args:
            config: Authentication configuration

        Returns:
            AuthMiddleware instance
        """
        providers = []

        # GitHub OAuth
        github_config = config.get("github")
        if github_config:
            providers.append(GitHubAuthProvider(GitHubOAuthConfig(**github_config)))

        # API Key
        api_key_config = config.get("api_key")
        if api_key_config and api_key_config.get("enabled"):
            providers.append(APIKeyAuthProvider(APIKeyConfig(**api_key_config)))

        # Dev mode
        dev_config = config.get("dev")
        if dev_config and dev_config.get("enabled"):
            providers.append(DevAuthProvider(DevAuthConfig(**dev_config)))

        return cls(providers)


class AuthenticationError(Exception):
    """Authentication failed."""

    pass
