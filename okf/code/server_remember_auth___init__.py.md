---
type: Source Code
description: "Authentication providers."
resource: server/remember/auth/__init__.py
timestamp: 2026-07-10T02:44:33Z
---

#   init  

Source path: `server/remember/auth/__init__.py`

## Content

```python
"""Authentication providers."""

from remember.auth.base import AuthProvider, AuthResult
from remember.auth.github import GitHubAuthProvider
from remember.auth.api_key import APIKeyAuthProvider
from remember.auth.dev import DevAuthProvider
from remember.auth.tailscale import TailscaleAuthProvider
from remember.auth.google import GoogleAuthProvider
from remember.auth.microsoft import MicrosoftAuthProvider
from remember.auth.keycloak import KeycloakAuthProvider
from remember.auth.authentik import AuthentikAuthProvider
from remember.auth.dex import DexAuthProvider

__all__ = [
    "AuthProvider",
    "AuthResult",
    "GitHubAuthProvider",
    "APIKeyAuthProvider",
    "DevAuthProvider",
    "TailscaleAuthProvider",
    "GoogleAuthProvider",
    "MicrosoftAuthProvider",
    "KeycloakAuthProvider",
    "AuthentikAuthProvider",
    "DexAuthProvider",
]
```

*…truncated — full source at `server/remember/auth/__init__.py`*
