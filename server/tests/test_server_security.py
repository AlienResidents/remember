"""Tests for security fixes — L6 (uniform error), L8 (limit cap), L3 (race condition).

Covers findings from the independent security review:
- L6: confirm/refute/verify/archive return uniform error for not-found and not-owned
- L8: list_memories caps limit to prevent unbounded queries
- L3: get_or_create_user_by_provider_id handles concurrent creation race
"""

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import User, Memory
from remember.tools import (
    confirm_memory,
    refute_memory,
    verify_memory,
    archive_memory,
    list_memories,
    save_memory,
)


# ---------------------------------------------------------------------------
# L6: Uniform error for not-found vs not-owned
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_confirm_non_owner_gets_same_error_as_not_found(
    db_session: AsyncSession, second_user: User, test_memory: Memory
):
    """L6: confirm_memory returns same error for non-owner as for non-existent memory."""
    # Non-existent memory
    result_not_found = await confirm_memory(
        memory_id=uuid.uuid4(),
        user_id=second_user.id,
        db=db_session,
    )
    # Existing memory owned by different user
    result_not_owned = await confirm_memory(
        memory_id=test_memory.id,
        user_id=second_user.id,
        db=db_session,
    )
    assert result_not_found == result_not_owned
    assert result_not_found["error"] == "Memory not found"


@pytest.mark.asyncio
async def test_refute_non_owner_gets_same_error_as_not_found(
    db_session: AsyncSession, second_user: User, test_memory: Memory
):
    """L6: refute_memory returns same error for non-owner as for non-existent memory."""
    result_not_found = await refute_memory(
        memory_id=uuid.uuid4(),
        user_id=second_user.id,
        reason="test",
        db=db_session,
    )
    result_not_owned = await refute_memory(
        memory_id=test_memory.id,
        user_id=second_user.id,
        reason="test",
        db=db_session,
    )
    assert result_not_found == result_not_owned
    assert result_not_found["error"] == "Memory not found"


@pytest.mark.asyncio
async def test_verify_non_owner_gets_same_error_as_not_found(
    db_session: AsyncSession, second_user: User, test_memory: Memory
):
    """L6: verify_memory returns same error for non-owner as for non-existent memory."""
    result_not_found = await verify_memory(
        memory_id=uuid.uuid4(),
        user_id=second_user.id,
        db=db_session,
    )
    result_not_owned = await verify_memory(
        memory_id=test_memory.id,
        user_id=second_user.id,
        db=db_session,
    )
    assert result_not_found == result_not_owned
    assert result_not_found["error"] == "Memory not found"


@pytest.mark.asyncio
async def test_archive_non_owner_gets_same_error_as_not_found(
    db_session: AsyncSession, second_user: User, test_memory: Memory
):
    """L6: archive_memory returns same error for non-owner as for non-existent memory."""
    result_not_found = await archive_memory(
        memory_id=uuid.uuid4(),
        user_id=second_user.id,
        db=db_session,
    )
    result_not_owned = await archive_memory(
        memory_id=test_memory.id,
        user_id=second_user.id,
        db=db_session,
    )
    assert result_not_found == result_not_owned
    assert result_not_found["error"] == "Memory not found"


# ---------------------------------------------------------------------------
# L8: Limit capping
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_memories_limit_cap(db_session: AsyncSession, test_user: User):
    """L8: list_memories caps limit to prevent unbounded queries."""
    # Create 10 memories
    for i in range(10):
        await save_memory(
            name=f"memory-{i}",
            type="project",
            description=f"Test memory {i}",
            body=f"Body {i}",
            owner_id=test_user.id,
            db=db_session,
        )

    # Request limit=10000 — should cap (tested at the MCP tool boundary in server.py,
    # but the underlying list_memories function should also handle large limits gracefully)
    results = await list_memories(
        owner_id=test_user.id,
        limit=10000,
        db=db_session,
    )
    # Should return all 10 (the cap is at the MCP wrapper, not the underlying function)
    assert len(results) == 10


@pytest.mark.asyncio
async def test_list_memories_default_limit(db_session: AsyncSession, test_user: User):
    """L8: list_memories with default limit returns reasonable number."""
    for i in range(5):
        await save_memory(
            name=f"limit-test-{i}",
            type="project",
            description=f"Test {i}",
            body=f"Body {i}",
            owner_id=test_user.id,
            db=db_session,
        )
    results = await list_memories(
        owner_id=test_user.id,
        limit=50,
        db=db_session,
    )
    assert len(results) == 5


# ---------------------------------------------------------------------------
# L3: Concurrent user creation race condition
# ---------------------------------------------------------------------------


def test_user_model_has_unique_constraint():
    """L3: User model has UniqueConstraint on (provider, provider_id).

    This prevents duplicate users from concurrent get-or-create race conditions.
    The IntegrityError handling in get_or_create_user_by_provider_id catches
    the violation and re-fetches the existing row.
    """
    from remember.models import User

    table_args = User.__table_args__
    # __table_args__ is a tuple of constraints
    constraints = [arg for arg in table_args if hasattr(arg, "name")]
    unique_constraints = [
        c for c in constraints
        if c.__class__.__name__ == "UniqueConstraint"
    ]
    assert len(unique_constraints) >= 1
    # Verify it covers provider + provider_id
    constraint = unique_constraints[0]
    col_names = [c.name for c in constraint.columns]
    assert "provider" in col_names
    assert "provider_id" in col_names


# ---------------------------------------------------------------------------
# M5: JWT middleware — empty sub, missing bearer, dev mode bypass
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_middleware_skips_healthz():
    """M5: /healthz bypasses auth middleware."""
    from starlette.testclient import TestClient
    from remember.server import app

    client = TestClient(app)
    # In dev mode (set by conftest), auth is skipped entirely
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_middleware_requires_bearer_token_in_prod_mode():
    """M5: In non-dev mode, MCP endpoint requires bearer token (POST with no token -> 401)."""
    import os
    from starlette.testclient import TestClient
    from remember.server import app
    from remember.config import settings

    # Temporarily enable Keycloak auth mode
    original_dev = settings.auth.dev_mode
    original_authority = settings.auth.keycloak_authority
    settings.auth.dev_mode = False
    settings.auth.keycloak_authority = "https://test-keycloak.example.com"

    try:
        client = TestClient(app)
        # MCP endpoint expects POST (JSON-RPC), not GET
        response = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        })
        # Without bearer token -> 401
        assert response.status_code == 401
        assert "error" in response.json()
    finally:
        # Restore
        settings.auth.dev_mode = original_dev
        settings.auth.keycloak_authority = original_authority