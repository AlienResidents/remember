---
type: auth
title: Dev Mode
description: Development mode that skips authentication for local development.
resource: server/remember/auth/dev.py
tags: [auth, dev, local]
timestamp: 2026-07-06T00:00:00Z
---

# Dev Mode

## Overview

Skips authentication entirely. Creates a default dev user on first request. For development only — never enable in production.

## Configuration

```yaml
dev:
  enabled: true
```

## Flow

1. Any request is accepted
2. Default dev user created/returned
3. `provider='dev'` in `users` table

## Related Concepts

* [Auth Middleware](middleware.md)
