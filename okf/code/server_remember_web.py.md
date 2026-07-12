---
type: Source Code
description: "Web UI server for REMEMBER."
resource: server/remember/web.py
timestamp: 2026-07-12T02:15:00Z
---

# web

Source path: `server/remember/web.py`

## Content

```python
"""Web UI server for REMEMBER.

Browser-based OAuth flow via Keycloak (authorization_code + PKCE grant):
  1. User visits / → static UI shell loads (no sensitive data)
  2. JS calls /api/* → 401 if not authenticated → JS redirects to /login?next=<current URL>
  3. /login → store `next` in session → redirect to Keycloak (PKCE challenge)
  4. User logs in at Keycloak → redirected back to /auth/callback
  5. /auth/callback → exchange code+PKCE verifier → store session → redirect to `next` (default /)
  6. JS retries /api/* with session cookie → succeeds

Security:
- PKCE (S256) protects against authorization-code interception even for
  confidential clients (RFC 9700 / OAuth 2.1 recommendation).
- OAuth `state` parameter prevents login CSRF (random, single-use, session-stored).
- `next` param validated by _safe_redirect_path to prevent open-redirect attacks
  (only same-origin relative paths allowed; //evil.com/ and https://evil.com/ → /).
- Session cookies are signed + encrypted by SessionMiddleware using session_secret.
- Access tokens stored in session, used for DB operations.

Identity: uses the Keycloak `sub` (OIDC subject) as provider_id — same as the
MCP path. WARNING: this assumes Keycloak uses PUBLIC subject identifiers
(same UUID across all clients for one user). If pairwise subjects are enabled
on either the `remember-web` or `remember-pi-oauth` client, the two paths will
get different `sub` values for the same human, and identity convergence breaks
silently. Do NOT enable pairwise subjects on either client.
"""

import json
import os
import secrets
import uuid
from pathlib import Path
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

from remember.config import settings
from remember.db import async_session_factory
from remember.models import User
from remember.tools import (
    search_memories,
    save_memory,
    get_memory,
    list_memories,
    verify_memory,
    archive_memory,
    refute_memory,
```

*…truncated — full source at `server/remember/web.py`*

## Key functions

- `_redirect_uri()` — Keycloak callback URL (env-configurable, defaults to `https://remember.cdd.net.au/auth/callback`).
- `_safe_redirect_path(path)` — validates a `next` redirect target is a safe relative path. Rejects `None`, empty, non-`/`-prefixed, `//evil.com` (protocol-relative), `/\\evil.com` (backslash). Returns `/` on rejection. Prevents open-redirect attacks on the `/login?next=` flow.
- `login(request, next)` — accepts optional `next` query param, stores it in session as `oauth_next`, redirects to Keycloak.
- `auth_callback(request)` — exchanges code for tokens, reads `oauth_next` from session, redirects to `_safe_redirect_path(next)`.