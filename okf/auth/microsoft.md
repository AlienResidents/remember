---
type: auth
title: Microsoft OAuth
description: Microsoft/Entra ID OAuth2 authentication provider.
resource: server/remember/auth/microsoft.py
tags: [auth, microsoft, oauth2, entra-id]
timestamp: 2026-07-06T00:00:00Z
---

# Microsoft OAuth

## Overview

Authenticates users via Microsoft/Entra ID OAuth2.

## Configuration

```yaml
microsoft:
  client_id: "${MICROSOFT_CLIENT_ID}"
  client_secret: "${MICROSOFT_CLIENT_SECRET}"
  tenant_id: "${MICROSOFT_TENANT_ID}"  # "common" for multi-tenant
  redirect_uri: "https://remember.example.com/auth/callback"
```

## Flow

Same as GitHub OAuth — standard OAuth2 authorization code flow with Microsoft token endpoint.

## Related Concepts

* [Auth Middleware](middleware.md)
