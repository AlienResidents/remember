---
type: auth
title: Keycloak
description: Self-hosted Keycloak OAuth2/OIDC authentication provider.
resource: server/remember/auth/keycloak.py
tags: [auth, keycloak, oidc, self-hosted]
timestamp: 2026-07-06T00:00:00Z
---

# Keycloak

## Overview

Authenticates users via self-hosted Keycloak OAuth2/OIDC. Supports any Keycloak realm.

## Configuration

```yaml
keycloak:
  enabled: true
  authority: "https://keycloak.example.com"
  realm: "remember"
  client_id: "${KEYCLOAK_CLIENT_ID}"
  client_secret: "${KEYCLOAK_CLIENT_SECRET}"
  redirect_uri: "https://remember.example.com/auth/callback"
```

## Flow

Standard OAuth2 authorization code flow against Keycloak's OIDC endpoints:
- Token endpoint: `{authority}/realms/{realm}/protocol/openid-connect/token`
- Userinfo endpoint: `{authority}/realms/{realm}/protocol/openid-connect/userinfo`

## Related Concepts

* [Auth Middleware](middleware.md)
* [Authentik](authentik.md)
* [Dex](dex.md)
