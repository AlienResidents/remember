---
type: auth
title: Auth Middleware
description: Pluggable authentication middleware that registers and routes between multiple identity providers.
resource: server/remember/auth/middleware.py
tags: [auth, middleware, pluggable]
timestamp: 2026-07-06T00:00:00Z
---

# Auth Middleware

## Overview

Central authentication middleware that manages multiple identity providers. Providers are registered via `from_config()` and attempted in order until one succeeds.

## Provider Registration Order

1. GitHub OAuth
2. Google OAuth
3. Microsoft/Entra ID
4. Keycloak
5. Authentik
6. Dex
7. Tailscale
8. API Key
9. Dev Mode

## Configuration

```python
from remember.auth.middleware import AuthMiddleware

config = {
    "github": {"client_id": "...", "client_secret": "..."},
    "google": {"client_id": "...", "client_secret": "..."},
    "microsoft": {"client_id": "...", "client_secret": "...", "tenant_id": "..."},
    "keycloak": {"enabled": True, "authority": "...", "realm": "...", "client_id": "...", "client_secret": "..."},
    "authentik": {"enabled": True, "authority": "...", "client_id": "...", "client_secret": "..."},
    "dex": {"enabled": True, "authority": "...", "client_id": "...", "client_secret": "..."},
    "tailscale": {"enabled": True, "tailnet": "..."},
    "api_key": {"enabled": True, "key": "..."},
    "dev": {"enabled": True},
}

middleware = AuthMiddleware.from_config(config)
```

## Authentication Flow

1. Request arrives with credentials (OAuth code, API key, tailnet user, etc.)
2. Middleware iterates through providers in registration order
3. First provider to successfully authenticate returns an `AuthResult`
4. If no provider succeeds, raises `AuthenticationError`

## Related Concepts

* [GitHub OAuth](github.md)
* [Google OAuth](google.md)
* [Microsoft OAuth](microsoft.md)
* [Tailscale Identity](tailscale.md)
* [Keycloak](keycloak.md)
* [Authentik](authentik.md)
* [Dex](dex.md)
* [API Key](api_key.md)
* [Dev Mode](dev.md)
