"""Authentication providers."""

from remember.auth.base import AuthProvider, AuthResult
from remember.auth.github import GitHubAuthProvider
from remember.auth.api_key import APIKeyAuthProvider
from remember.auth.dev import DevAuthProvider
from remember.auth.tailscale import TailscaleAuthProvider
from remember.auth.google import GoogleAuthProvider
from remember.auth.microsoft import MicrosoftAuthProvider

__all__ = [
    "AuthProvider",
    "AuthResult",
    "GitHubAuthProvider",
    "APIKeyAuthProvider",
    "DevAuthProvider",
    "TailscaleAuthProvider",
    "GoogleAuthProvider",
    "MicrosoftAuthProvider",
]
