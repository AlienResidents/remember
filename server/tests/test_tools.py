"""Tests for MCP tools."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import User, Memory
from remember.tools import (
    search_memories,
    save_memory,
    get_memory,
    list_memories,
    get_stale_memories,
    verify_memory,
    archive_memory,
    confirm_memory,
    refute_memory,
)


@pytest.mark.asyncio
async def test_save_memory(db_session: AsyncSession, test_user: User):
    """Test saving a new memory."""
    result = await save_memory(
        name="test-save",
        type="project",
        description="Test save",
        body="# Test\n\nBody content",
        owner_id=test_user.id,
        db=db_session,
    )

    assert "id" in result
    assert result["message"] == "Memory saved successfully"

    # Verify memory was created
    stmt = select(Memory).where(Memory.name == "test-save")
    query = await db_session.execute(stmt)
    memory = query.scalar_one_or_none()
    assert memory is not None
    assert memory.type == "project"


@pytest.mark.asyncio
async def test_save_memory_update(db_session: AsyncSession, test_user: User):
    """Test updating an existing memory."""
    # Create initial memory
    await save_memory(
        name="test-update",
        type="project",
        description="Original",
        body="# Original\n\nBody",
        owner_id=test_user.id,
        db=db_session,
    )

    # Update memory
    result = await save_memory(
        name="test-update",
        type="project",
        description="Updated",
        body="# Updated\n\nNew body",
        owner_id=test_user.id,
        db=db_session,
    )

    assert result["message"] == "Memory saved successfully"

    # Verify update
    stmt = select(Memory).where(Memory.name == "test-update")
    query = await db_session.execute(stmt)
    memory = query.scalar_one_or_none()
    assert memory.description == "Updated"
    assert memory.body == "# Updated\n\nNew body"


@pytest.mark.asyncio
async def test_get_memory(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test getting a memory."""
    result = await get_memory(
        memory_id=test_memory.id,
        user_id=test_user.id,
        db=db_session,
    )

    assert result is not None
    assert result["id"] == str(test_memory.id)
    assert result["name"] == "test-memory"
    assert result["body"] == "# Test Memory\n\nThis is a test."


@pytest.mark.asyncio
async def test_get_memory_not_found(db_session: AsyncSession, test_user: User):
    """Test getting a non-existent memory."""
    result = await get_memory(
        memory_id=uuid.uuid4(),
        user_id=test_user.id,
        db=db_session,
    )

    assert result is None


@pytest.mark.asyncio
async def test_list_memories(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test listing memories."""
    result = await list_memories(
        owner_id=test_user.id,
        db=db_session,
    )

    assert len(result) >= 1
    assert any(m["name"] == "test-memory" for m in result)


@pytest.mark.asyncio
@pytest.mark.skip(reason="search_memories uses PostgreSQL to_tsvector; not compatible with SQLite test DB")
async def test_search_memories(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test searching memories."""
    result = await search_memories(
        query="test",
        db=db_session,
    )

    assert len(result) >= 1
    assert any(m["name"] == "test-memory" for m in result)


@pytest.mark.asyncio
async def test_verify_memory(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test verifying a memory."""
    result = await verify_memory(
        memory_id=test_memory.id,
        user_id=test_user.id,
        db=db_session,
    )

    assert result["message"] == "Memory verified successfully"

    # Verify last_verified_at was updated
    stmt = select(Memory).where(Memory.id == test_memory.id)
    query = await db_session.execute(stmt)
    memory = query.scalar_one_or_none()
    assert memory.last_verified_at is not None


@pytest.mark.asyncio
async def test_verify_memory_not_owner(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test verifying a memory as non-owner."""
    other_user = User(
        id=uuid.uuid4(),
        provider="github",
        provider_id="other",
        display_name="Other User",
    )
    db_session.add(other_user)
    await db_session.commit()

    result = await verify_memory(
        memory_id=test_memory.id,
        user_id=other_user.id,
        db=db_session,
    )

    assert "error" in result


@pytest.mark.asyncio
async def test_archive_memory(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test archiving a memory."""
    result = await archive_memory(
        memory_id=test_memory.id,
        user_id=test_user.id,
        db=db_session,
    )

    assert result["message"] == "Memory archived successfully"

    # Verify status was updated
    stmt = select(Memory).where(Memory.id == test_memory.id)
    query = await db_session.execute(stmt)
    memory = query.scalar_one_or_none()
    assert memory.status == "archived"


@pytest.mark.asyncio
async def test_confirm_memory(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test confirming a memory."""
    result = await confirm_memory(
        memory_id=test_memory.id,
        user_id=test_user.id,
        note="This is accurate",
        db=db_session,
    )

    assert result["message"] == "Memory confirmed successfully"


@pytest.mark.asyncio
async def test_refute_memory(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test refuting a memory."""
    result = await refute_memory(
        memory_id=test_memory.id,
        user_id=test_user.id,
        reason="This is incorrect",
        db=db_session,
    )

    assert result["message"] == "Memory refuted successfully"

    # Verify status was updated to disputed
    stmt = select(Memory).where(Memory.id == test_memory.id)
    query = await db_session.execute(stmt)
    memory = query.scalar_one_or_none()
    assert memory.status == "disputed"
