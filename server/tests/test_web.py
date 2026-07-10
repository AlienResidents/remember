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
async def test_api_search_no_auth():
    """Test search endpoint without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/search?q=test")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_get_no_auth():
    """Test get endpoint without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/get/test-id")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_save_no_auth():
    """Test save endpoint without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/save",
            json={"name": "test", "type": "test", "description": "test", "body": "test"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_verify_no_auth():
    """Test verify endpoint without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/verify/test-id")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_archive_no_auth():
    """Test archive endpoint without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/archive/test-id")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_refute_no_auth():
    """Test refute endpoint without auth returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/refute/test-id", json={"reason": "test"})
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_status_unauthenticated():
    """Test auth status endpoint returns unauthenticated without session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False