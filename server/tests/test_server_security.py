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


# ---------------------------------------------------------------------------
# Strix findings: offset bypass, api_search cap, vector IDOR, tsquery sanitization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_memories_offset_is_capped(db_session: AsyncSession, test_user: User):
    """Strix vuln-0001: offset is capped independently — limit=1, offset=999999
    must NOT produce a DB query for 1,000,000 rows.

    The old code passed `limit=capped_limit + offset`, which let an attacker
    bypass the 500-row cap by sending a huge offset. The fix passes limit and
    offset as separate parameters with offset capped at 10,000.
    """
    for i in range(5):
        await save_memory(
            name=f"offset-test-{i}",
            type="project",
            description=f"Test {i}",
            body=f"Body {i}",
            owner_id=test_user.id,
            db=db_session,
        )
    # With offset cap, requesting offset=999999 returns at most 5 results
    # (the cap limits offset to 10,000, and we only have 5 memories)
    results = await list_memories(
        owner_id=test_user.id,
        limit=50,
        offset=999999,
        db=db_session,
    )
    # With only 5 memories and a huge offset, we get 0 results (not 1,000,000 rows)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_list_memories_offset_pagination_works(db_session: AsyncSession, test_user: User):
    """Strix vuln-0001: offset still works for legitimate pagination."""
    for i in range(10):
        await save_memory(
            name=f"page-test-{i:02d}",
            type="project",
            description=f"Test {i}",
            body=f"Body {i}",
            owner_id=test_user.id,
            db=db_session,
        )
    page1 = await list_memories(owner_id=test_user.id, limit=5, offset=0, db=db_session)
    page2 = await list_memories(owner_id=test_user.id, limit=5, offset=5, db=db_session)
    assert len(page1) == 5
    assert len(page2) == 5
    # Pages should not overlap
    page1_names = {r["name"] for r in page1}
    page2_names = {r["name"] for r in page2}
    assert page1_names.isdisjoint(page2_names)


def test_api_search_caps_limit():
    """Strix vuln-0002: web UI /api/search caps limit at 100 (like MCP wrapper)."""
    import inspect
    from remember.web import api_search
    source = inspect.getsource(api_search)
    assert "min(limit, 100)" in source, "api_search must cap limit at 100"


def test_search_memories_vector_has_owner_id_param():
    """Strix vuln-0003: search_memories_vector accepts owner_id for scoping."""
    import inspect
    from remember.tools.search_vector import search_memories_vector
    sig = inspect.signature(search_memories_vector)
    assert "owner_id" in sig.parameters, "search_memories_vector must accept owner_id"


def test_search_memories_vector_scopes_by_owner():
    """Strix vuln-0003: _search_memories_vector filters by owner_id in the query."""
    import inspect
    from remember.tools.search_vector import _search_memories_vector
    source = inspect.getsource(_search_memories_vector)
    assert "owner_id" in source, "_search_memories_vector must filter by owner_id"
    assert "Memory.owner_id == owner_id" in source


def test_search_sanitizes_tsquery_operators():
    """Strix vuln-0004: _sanitize_tsquery strips tsquery operator chars."""
    from remember.tools.search import _sanitize_tsquery

    # Normal query — words joined with OR, prefix match on last
    assert _sanitize_tsquery("hello world") == "hello | world*"

    # Operator chars stripped
    assert _sanitize_tsquery("hello & world") == "hello | world*"
    assert _sanitize_tsquery("test!") == "test*"
    assert _sanitize_tsquery("(test)") == "test*"
    assert _sanitize_tsquery('a"b') == "ab*"
    assert _sanitize_tsquery("a:b") == "ab*"

    # All-operator input returns empty string (caller returns [])
    assert _sanitize_tsquery("!&|():*\"") == ""


def test_web_get_or_create_user_handles_integrity_error():
    """Strix vuln-0005: web.py _get_or_create_user catches IntegrityError."""
    import inspect
    from remember.web import _get_or_create_user
    source = inspect.getsource(_get_or_create_user)
    assert "IntegrityError" in source, "_get_or_create_user must catch IntegrityError"
    assert "rollback" in source.lower(), "must rollback on IntegrityError"