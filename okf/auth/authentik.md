---
type: auth
title: Authentik
description: Self-hosted Authentik OAuth2 authentication provider.
resource: server/remember/auth/authentik.py
tags: [auth, authentik, self-hosted]
timestamp: 2026-07-06T00:00:00Z
---

# Authentik

## Overview

Authenticates users via self-hosted Authentik OAuth2.

## Configuration

```yaml
authentik:
  enabled: true
  authority: "https://authentik.example.com"
  client_id: "${AUTHENTIK_CLIENT_ID}"
  client_secret: "${AUTHENTIK_CLIENT_SECRET}"
  redirect_uri: "https://remember.example.com/auth/callback"
```

## Flow

Standard OAuth2 authorization code flow against Authentik's token and userinfo endpoints.

## Related Concepts

* [Auth Middleware](middleware.md)
* [Keycloak](keycloak.md)
* [Dex](dex.md)
