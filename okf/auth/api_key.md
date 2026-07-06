---
type: auth
title: API Key
description: Static API key authentication for CI/CD and automation.
resource: server/remember/auth/api_key.py
tags: [auth, api-key, ci-cd]
timestamp: 2026-07-06T00:00:00Z
---

# API Key

## Overview

Authenticates requests using a static API key. Useful for CI/CD pipelines and automation.

## Configuration

```yaml
api_key:
  enabled: true
  key: "${REMEMBER_API_KEY}"
```

## Flow

1. Request includes `Authorization: Bearer <key>` header
2. Provider validates key matches configured value
3. User created/updated in `users` table with `provider='api_key'`

## Related Concepts

* [Auth Middleware](middleware.md)
