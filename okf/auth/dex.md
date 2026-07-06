---
type: auth
title: Dex
description: Dex OIDC provider for Kubernetes environments.
resource: server/remember/auth/dex.py
tags: [auth, dex, oidc, kubernetes]
timestamp: 2026-07-06T00:00:00Z
---

# Dex

## Overview

Authenticates users via Dex OIDC provider, commonly used in Kubernetes environments.

## Configuration

```yaml
dex:
  enabled: true
  authority: "https://dex.example.com"
  client_id: "${DEX_CLIENT_ID}"
  client_secret: "${DEX_CLIENT_SECRET}"
  redirect_uri: "https://remember.example.com/auth/callback"
```

## Flow

Standard OAuth2 authorization code flow against Dex endpoints:
- Token endpoint: `{authority}/dex/token`
- Userinfo endpoint: `{authority}/dex/userinfo`

## Related Concepts

* [Auth Middleware](middleware.md)
* [Keycloak](keycloak.md)
* [Authentik](authentik.md)
