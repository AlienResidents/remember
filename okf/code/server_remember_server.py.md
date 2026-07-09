---
type: Source Code
description: "REMEMBER FastMCP server."
resource: server/remember/server.py
timestamp: 2026-07-09T13:05:53Z
---

# server

Source path: `server/remember/server.py`

## Content

```python
"""REMEMBER FastMCP server."""

import asyncio
import logging
from contextlib import asynccontextmanager

import jwt
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

import uuid as uuid_module
from datetime import datetime

from remember.config import settings
from remember.db import init_db, close_db
from remember.tools import (
    search_memories as _search_memories,
    save_memory as _save_memory,
    get_memory as _get_memory,
    list_memories as _list_memories,
    get_stale_memories as _get_stale_memories,
    verify_memory as _verify_memory,
    archive_memory as _archive_memory,
    confirm_memory as _confirm_memory,
    refute_memory as _refute_memory,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "remember",
    instructions="Team memory system for collaborative knowledge sharing.",
)


@asynccontextmanager
async def server_lifespan(server: FastMCP):
```

*…truncated — full source at `server/remember/server.py`*
