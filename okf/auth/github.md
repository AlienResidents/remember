---
type: auth
title: GitHub OAuth
description: GitHub OAuth2 authentication provider for team member identification.
resource: server/remember/auth/github.py
tags: [auth, github, oauth2]
timestamp: 2026-07-06T00:00:00Z
---

# GitHub OAuth

## Overview

Authenticates users via GitHub OAuth2. Maps GitHub usernames to `users` table rows.

## Configuration

```yaml
github:
  client_id: "${GITHUB_CLIENT_ID}"
  client_secret: "${GITHUB_CLIENT_SECRET}"
  redirect_uri: "https://remember.example.com/auth/callback"
```

## Flow

1. User clicks "Sign in with GitHub"
2. Redirected to GitHub OAuth consent screen
3. GitHub redirects back with authorization code
4. Server exchanges code for access token
5. Server fetches user info from GitHub API
6. User created/updated in `users` table with `provider='github'`

## Related Concepts

* [Auth Middleware](middleware.md)
