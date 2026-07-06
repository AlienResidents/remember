---
type: auth
title: Google OAuth
description: Google OAuth2 authentication provider.
resource: server/remember/auth/google.py
tags: [auth, google, oauth2]
timestamp: 2026-07-06T00:00:00Z
---

# Google OAuth

## Overview

Authenticates users via Google OAuth2.

## Configuration

```yaml
google:
  client_id: "${GOOGLE_CLIENT_ID}"
  client_secret: "${GOOGLE_CLIENT_SECRET}"
  redirect_uri: "https://remember.example.com/auth/callback"
```

## Flow

Same as GitHub OAuth — standard OAuth2 authorization code flow.

## Related Concepts

* [Auth Middleware](middleware.md)
