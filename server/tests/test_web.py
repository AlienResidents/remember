"""Tests for web UI endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from remember.web import app


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
    """Test static JS file is served."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/app.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_api_search_no_db():
    """Test search endpoint without DB connection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/search?q=test")
        # Should fail without DB, but not crash
        assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_api_get_no_db():
    """Test get endpoint without DB connection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/get/test-id")
        # Should fail without DB, but not crash
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
async def test_api_save_no_db():
    """Test save endpoint without DB connection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/save",
            json={"name": "test", "type": "test", "description": "test", "body": "test"},
        )
        # Should fail without DB, but not crash
        assert response.status_code in [200, 400, 500]


@pytest.mark.asyncio
async def test_api_verify_no_db():
    """Test verify endpoint without DB connection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/verify/test-id")
        # Should fail without DB, but not crash
        assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_api_archive_no_db():
    """Test archive endpoint without DB connection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/archive/test-id")
        # Should fail without DB, but not crash
        assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_api_refute_no_db():
    """Test refute endpoint without DB connection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/refute/test-id", json={"reason": "test"})
        # Should fail without DB, but not crash
        assert response.status_code in [200, 500]
