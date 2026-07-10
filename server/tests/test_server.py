"""Tests for server startup and health."""

import pytest
from starlette.testclient import TestClient

from remember.server import app


def test_healthz():
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_mcp_endpoint_requires_post():
    """Test that GET on /mcp returns 405 (MCP uses POST for JSON-RPC)."""
    client = TestClient(app)
    response = client.get("/mcp")
    assert response.status_code == 405


def test_mcp_requires_bearer_token_in_prod_mode():
    """Test that POST /mcp without token returns 401 in non-dev mode."""
    from remember.config import settings

    original_dev = settings.auth.dev_mode
    original_authority = settings.auth.keycloak_authority
    settings.auth.dev_mode = False
    settings.auth.keycloak_authority = "https://test-keycloak.example.com"

    try:
        client = TestClient(app)
        response = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        })
        assert response.status_code == 401
    finally:
        settings.auth.dev_mode = original_dev
        settings.auth.keycloak_authority = original_authority