---
type: Source Code
description: "Tests for server startup and health."
resource: server/tests/test_server.py
timestamp: 2026-07-09T14:09:54Z
---

# test server

Source path: `server/tests/test_server.py`

## Content

```python
"""Tests for server startup and health."""

import pytest
from httpx import AsyncClient, ASGITransport

from remember.server import app


@pytest.mark.asyncio
async def test_healthz():
    """Test health check endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_returns_mcp_info():
    """Test root endpoint returns MCP info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data


@pytest.mark.asyncio
async def test_mcp_tools_endpoint():
    """Test MCP tools listing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/mcp")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) > 0


@pytest.mark.asyncio
```

*…truncated — full source at `server/tests/test_server.py`*
