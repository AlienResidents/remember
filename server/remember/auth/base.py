"""Base authentication provider."""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AuthResult:
    """Result of authentication."""

    user_id: uuid.UUID
    provider: str
    provider_id: str
    display_name: str
    email: str | None = None


class AuthProvider(ABC):
    """Base authentication provider."""

    @abstractmethod
    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate a user.

        Args:
            **kwargs: Provider-specific credentials

        Returns:
            AuthResult with user information

        Raises:
            AuthenticationError: If authentication fails
        """
        ...

    @abstractmethod
    def get_callback_url(self) -> str:
        """Get the OAuth callback URL.

        Returns:
            Callback URL for OAuth flows
        """
        ...
