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
        data = response.json()
        assert data["status"] == "healthy"
        print(f"   ✓ Health check: {data}")

        # Test index
        print("\n2. Testing /...")
        response = await client.get("/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/html" in response.headers["content-type"]
        assert "REMEMBER" in response.text
        print(f"   ✓ Index page served ({len(response.text)} bytes)")

        # Test static CSS
        print("\n3. Testing /styles.css...")
        response = await client.get("/styles.css")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/css" in response.headers["content-type"]
        print(f"   ✓ CSS served ({len(response.text)} bytes)")

        # Test static JS
        print("\n4. Testing /app.js...")
        response = await client.get("/app.js")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "javascript" in response.headers["content-type"]
        print(f"   ✓ JS served ({len(response.text)} bytes)")

        # Test API endpoints (will fail without DB, but should not crash)
        print("\n5. Testing API endpoints (expect failures without DB)...")
        endpoints = [
            ("GET", "/api/search?q=test"),
            ("GET", "/api/get/test-id"),
            ("POST", "/api/save", {"name": "test", "type": "test", "description": "test", "body": "test"}),
            ("POST", "/api/verify/test-id"),
            ("POST", "/api/archive/test-id"),
            ("POST", "/api/refute/test-id", {"reason": "test"}),
        ]

        for method, path, *body in endpoints:
            kwargs = {}
            if body:
                kwargs["json"] = body[0]
            response = await getattr(client, method.lower())(path, **kwargs)
            print(f"   {method} {path}: {response.status_code}")

    print("\n" + "=" * 60)
    print("All tests passed! ✓")


if __name__ == "__main__":
    asyncio.run(test_webui())
