---
type: Source Code
description: "Web UI server for REMEMBER."
resource: server/remember/web.py
timestamp: 2026-07-09T01:43:40Z
---

# web

Source path: `server/remember/web.py`

## Content

```python
"""Web UI server for REMEMBER."""

import json
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from remember.db import async_session_factory
from remember.models import Memory
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

# Serve static files at root (index.html served automatically via html=True)
# webui_path can be overridden for testing (e.g., tests/dev_test_webui.py)
app.webui_path = Path(__file__).parent.parent / "webui"
app.mount("/", StaticFiles(directory=str(app.webui_path), html=True), name="static")


@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"status": "healthy", "service": "remember-webui"}


@app.get("/api/search")
async def api_search(
    q: str,
    type: str | None = None,
    status: str | None = None,
```

*…truncated — full source at `server/remember/web.py`*
