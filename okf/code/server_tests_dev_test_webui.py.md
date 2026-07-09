---
type: Source Code
description: "!/usr/bin/env python3"
resource: server/tests/dev_test_webui.py
timestamp: 2026-07-09T13:54:50Z
---

# dev test webui

Source path: `server/tests/dev_test_webui.py`

## Content

```python
#!/usr/bin/env python3
"""Dev testing script for web UI.

Run this script to test the web UI locally without deploying to k8s.
Requires the remember-server package to be installed in the current environment.

Usage:
    python -m tests.dev_test_webui
"""

import asyncio
import sys
from pathlib import Path

# Add server dir to path
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir))

from httpx import AsyncClient, ASGITransport
from fastapi.staticfiles import StaticFiles

# Override webui_path for local testing before importing
import remember.web
remember.web.app.webui_path = server_dir / "webui"
# Re-mount static files with correct path
remember.web.app.mount("/", StaticFiles(directory=str(remember.web.app.webui_path), html=True), name="static")

from remember.web import app


async def test_webui():
    """Test all web UI endpoints."""
    print("Testing REMEMBER Web UI...")
    print("=" * 60)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test healthz
        print("\n1. Testing /healthz...")
        response = await client.get("/healthz")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
```

*…truncated — full source at `server/tests/dev_test_webui.py`*
