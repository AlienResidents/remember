---
type: Auth Base
title: Auth Base
description: Abstract base class and utilities for auth providers.
resource: server/remember/auth/base.py
tags: [auth, base, abstract]
timestamp: 2026-07-08T00:00:00Z
---

# Auth Base

Abstract base class for authentication providers.

## Purpose

Defines the interface that all auth providers must implement:

- `authenticate(token)` — validate credentials and return user identity
- `get_user_info(identity)` — fetch additional user details
- `logout()` — invalidate session

## Implementation

Concrete providers (GitHub, Google, Keycloak, etc.) extend this base class and override the abstract methods to implement provider-specific logic.

## Related

- [GitHub OAuth](github.md)
- [Google OAuth](google.md)
- [Keycloak](keycloak.md)
- [Auth Middleware](middleware.md)
