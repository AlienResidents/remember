---
type: auth
title: Tailscale Identity
description: Tailscale tailnet user authentication using tailnet identity.
resource: server/remember/auth/tailscale.py
tags: [auth, tailscale, identity]
timestamp: 2026-07-06T00:00:00Z
---

# Tailscale Identity

## Overview

Authenticates users by their Tailscale tailnet identity (e.g., `user@test.ts.net`). No OAuth flow — identity is extracted from the Tailscale network context.

## Configuration

```yaml
tailscale:
  enabled: true
  tailnet: "test.ts.net"
```

## Flow

1. Request arrives with `X-Tailscale-User` header or tailnet user identifier
2. Provider validates format (`user@tailnet.ts.net`)
3. User created/updated in `users` table with `provider='tailscale'`

## Related Concepts

* [Auth Middleware](middleware.md)
