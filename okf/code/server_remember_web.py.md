---
type: Source Code
description: "Web UI server for REMEMBER."
resource: server/remember/web.py
timestamp: 2026-07-09T13:05:53Z
---

# web

Source path: `server/remember/web.py`

## Content

```python
"""Web UI server for REMEMBER.

Browser-based OAuth flow via Keycloak (authorization_code grant):
  1. User visits / → static UI shell loads (no sensitive data)
  2. JS calls /api/* → 401 if not authenticated → JS redirects to /login
  3. /login → redirect to Keycloak authorization endpoint
  4. User logs in at Keycloak → redirected back to /auth/callback
  5. /auth/callback → exchange code for tokens → store in session cookie → redirect /
  6. JS retries /api/* with session cookie → succeeds

Session cookies are signed + encrypted by SessionMiddleware using session_secret.
Access tokens are stored in the session and used for DB operations.
"""

import json
import os
import uuid
from pathlib import Path
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

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
)

app = FastAPI(title="REMEMBER Web UI")
```

*…truncated — full source at `server/remember/web.py`*
