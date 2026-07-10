"""Tests for authorization — C2 (per-memory access control).

Verifies that tool functions scope results to the authenticated user:
- get_memory returns None for non-owner
- list_memories only returns the caller's memories
- get_stale_memories only returns the caller's stale memories
"""

import uuid
from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import User, Memory
from remember.tools import (
    get_memory,
    list_memories,
    get_stale_memories,
    save_memory,
    verify_memory,
    archive_memory,
)


@pytest.mark.asyncio
async def test_get_memory_owner_can_read(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """C2: Owner can read their own memory."""
    result = await get_memory(
        memory_id=test_memory.id,
        user_id=test_user.id,
        db=db_session,
    )
    assert result is not None
    assert result["id"] == str(test_memory.id)


@pytest.mark.asyncio
async def test_get_memory_non_owner_gets_none(
    db_session: AsyncSession, test_user: User, second_user: User, test_memory: Memory
):
    """C2: Non-owner cannot read another user's memory — returns None (not 403, to avoid leaking existence)."""
    result = await get_memory(
        memory_id=test_memory.id,
        user_id=second_user.id,
        db=db_session,
    )
    assert result is None


@pytest.mark.asyncio
async def test_list_memories_only_returns_own(
    db_session: AsyncSession, test_user: User, second_user: User, test_memory: Memory
):
    """C2: list_memories scoped to owner only returns the caller's memories."""
    # Create a memory owned by second_user
    await save_memory(
        name="other-user-memory",
        type="project",
        description="Belongs to other user",
        body="Secret content",
        owner_id=second_user.id,
        db=db_session,
    )

    # List as test_user — should only see test_user's memories
    results = await list_memories(
        owner_id=test_user.id,
        db=db_session,
    )
    assert all(m["owner_id"] == str(test_user.id) for m in results)
    assert any(m["name"] == "test-memory" for m in results)
    assert not any(m["name"] == "other-user-memory" for m in results)


@pytest.mark.asyncio
async def test_list_memories_as_other_user(
    db_session: AsyncSession, test_user: User, second_user: User, test_memory: Memory
):
    """C2: list_memories as second_user only returns second_user's memories."""
    # Create a memory owned by second_user
    await save_memory(
        name="other-user-memory",
        type="project",
        description="Belongs to other user",
        body="Secret content",
        owner_id=second_user.id,
        db=db_session,
    )

    # List as second_user — should only see second_user's memories
    results = await list_memories(
        owner_id=second_user.id,
        db=db_session,
    )
    assert all(m["owner_id"] == str(second_user.id) for m in results)
    assert any(m["name"] == "other-user-memory" for m in results)
    assert not any(m["name"] == "test-memory" for m in results)


@pytest.mark.asyncio
async def test_get_stale_memories_only_returns_own(
    db_session: AsyncSession, test_user: User, second_user: User, test_memory: Memory
):
    """C2: get_stale_memories scoped to owner only returns the caller's stale memories."""
    # Create a stale memory owned by second_user
    stale_memory = Memory(
        id=uuid.uuid4(),
        name="other-user-stale",
        type="project",
        description="Stale memory owned by other user",
        body="Secret stale content",
        owner_id=second_user.id,
        status="active",
        created_at=datetime.now(timezone.utc) - timedelta(days=120),
        updated_at=datetime.now(timezone.utc) - timedelta(days=120),
        last_verified_at=None,
    )
    db_session.add(stale_memory)
    await db_session.commit()

    # Get stale as test_user — should only see test_user's stale memories
    results = await get_stale_memories(
        threshold_days=90,
        owner_id=test_user.id,
        db=db_session,
    )
    assert all(m["owner_id"] == str(test_user.id) for m in results)
    assert not any(m["name"] == "other-user-stale" for m in results)


@pytest.mark.asyncio
async def test_verify_memory_non_owner_denied(
    db_session: AsyncSession, second_user: User, test_memory: Memory
):
    """C2: Non-owner cannot verify another user's memory."""
    result = await verify_memory(
        memory_id=test_memory.id,
        user_id=second_user.id,
        db=db_session,
    )
    assert "error" in result


@pytest.mark.asyncio
async def test_archive_memory_non_owner_denied(
    db_session: AsyncSession, second_user: User, test_memory: Memory
):
    """C2: Non-owner cannot archive another user's memory."""
    result = await archive_memory(
        memory_id=test_memory.id,
        user_id=second_user.id,
        db=db_session,
    )
    assert "error" in result