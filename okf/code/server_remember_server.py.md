---
type: Source Code
description: "REMEMBER FastMCP server."
resource: server/remember/server.py
timestamp: 2026-07-09T01:43:40Z
---

# server

Source path: `server/remember/server.py`

## Content

```python
"""REMEMBER FastMCP server."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from remember.config import settings
from remember.db import init_db, close_db
from remember.tools import (
    search_memories,
    save_memory,
    get_memory,
    list_memories,
    get_stale_memories,
    verify_memory,
    archive_memory,
    confirm_memory,
    refute_memory,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "remember",
    instructions="Team memory system for collaborative knowledge sharing.",
)


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Server lifespan handler."""
    logger.info("Starting REMEMBER server...")
    await init_db()
    logger.info("Database initialized")
    yield
```

*…truncated — full source at `server/remember/server.py`*
