---
type: Source Code
description: "Tests for web UI endpoints."
resource: server/tests/test_web.py
timestamp: 2026-07-12T02:15:00Z
---

# test web

Source path: `server/tests/test_web.py`

## Content

```python
"""Tests for web UI endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from remember.web import app, _safe_redirect_path


@pytest.mark.asyncio
async def test_healthz():
    """Test health check endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "remember-webui"


@pytest.mark.asyncio
async def test_index():
    """Test index page serves HTML."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "REMEMBER" in response.text


@pytest.mark.asyncio
async def test_static_css():
    """Test static CSS file is served."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_static_js():
```

*…truncated — full source at `server/tests/test_web.py`*

## Open-redirect prevention tests

Six tests cover `_safe_redirect_path()` — the validator that prevents open-redirect attacks on the `/login?next=` flow:

- `test_safe_redirect_path_accepts_relative` — valid relative paths pass through unchanged (`/?memory=abc-123`, `/memories`, `/`).
- `test_safe_redirect_path_rejects_external` — absolute URLs (`https://evil.com/`) → `/`.
- `test_safe_redirect_path_rejects_protocol_relative` — `//evil.com/` → `/` (browsers treat as `https://evil.com/`).
- `test_safe_redirect_path_rejects_backslash` — `/\\evil.com/` → `/` (some browsers treat `\\` as `/`).
- `test_safe_redirect_path_rejects_none_and_empty` — `None` and `""` → `/`.
- `test_safe_redirect_path_preserves_query_and_fragment` — query params and fragments on valid paths are preserved (`/?memory=abc-123&type=project`, `/?q=test&memory=def#section`).