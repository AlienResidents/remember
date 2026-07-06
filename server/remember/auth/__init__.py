"""Authentication providers."""

from remember.auth.base import AuthProvider, AuthResult
from remember.auth.github import GitHubAuthProvider
from remember.auth.api_key import APIKeyAuthProvider
from remember.auth.dev import DevAuthProvider

__all__ = [
    "AuthProvider",
    "AuthResult",
    "GitHubAuthProvider",
    "APIKeyAuthProvider",
    "DevAuthProvider",
]
