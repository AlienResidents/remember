"""Tests for database migrations."""

import pytest
from sqlalchemy import select

from remember.models import User, Memory, Tag, Confirmation, MemoryHistory, AccessLog


@pytest.mark.asyncio
async def test_db_init(patch_db):
    """Test database initialization (create_all is idempotent)."""
    from remember.db import init_db
    # Tables already created by db_session fixture (via patch_db dependency).
    # init_db calls create_all which is IF NOT EXISTS — safe to call again.
    await init_db()


@pytest.mark.asyncio
async def test_user_model(patch_db):
    """Test User model query."""
    from remember.db import async_session_factory
    async with async_session_factory() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        assert isinstance(users, list)


@pytest.mark.asyncio
async def test_memory_model(patch_db):
    """Test Memory model query."""
    from remember.db import async_session_factory
    async with async_session_factory() as db:
        result = await db.execute(select(Memory))
        memories = result.scalars().all()
        assert isinstance(memories, list)


@pytest.mark.asyncio
async def test_tag_model(patch_db):
    """Test Tag model query."""
    from remember.db import async_session_factory
    async with async_session_factory() as db:
        result = await db.execute(select(Tag))
        tags = result.scalars().all()
        assert isinstance(tags, list)


@pytest.mark.asyncio
async def test_confirmation_model(patch_db):
    """Test Confirmation model query."""
    from remember.db import async_session_factory
    async with async_session_factory() as db:
        result = await db.execute(select(Confirmation))
        confirmations = result.scalars().all()
        assert isinstance(confirmations, list)


@pytest.mark.asyncio
async def test_history_model(patch_db):
    """Test MemoryHistory model query."""
    from remember.db import async_session_factory
    async with async_session_factory() as db:
        result = await db.execute(select(MemoryHistory))
        histories = result.scalars().all()
        assert isinstance(histories, list)


@pytest.mark.asyncio
async def test_access_log_model(patch_db):
    """Test AccessLog model query."""
    from remember.db import async_session_factory
    async with async_session_factory() as db:
        result = await db.execute(select(AccessLog))
        logs = result.scalars().all()
        assert isinstance(logs, list)