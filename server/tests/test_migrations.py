"""Tests for database migrations."""

import pytest
import asyncio
from pathlib import Path

from remember.db import async_session_factory, init_db
from remember.models import User, Memory, Tag, Confirmation, History, AccessLog


@pytest.mark.asyncio
async def test_db_init():
    """Test database initialization."""
    # Should not raise
    await init_db()


@pytest.mark.asyncio
async def test_user_model():
    """Test User model creation."""
    async with async_session_factory() as db:
        from sqlalchemy import select
        result = await db.execute(select(User))
        users = result.scalars().all()
        assert isinstance(users, list)


@pytest.mark.asyncio
async def test_memory_model():
    """Test Memory model creation."""
    async with async_session_factory() as db:
        from sqlalchemy import select
        result = await db.execute(select(Memory))
        memories = result.scalars().all()
        assert isinstance(memories, list)


@pytest.mark.asyncio
async def test_tag_model():
    """Test Tag model creation."""
    async with async_session_factory() as db:
        from sqlalchemy import select
        result = await db.execute(select(Tag))
        tags = result.scalars().all()
        assert isinstance(tags, list)


@pytest.mark.asyncio
async def test_confirmation_model():
    """Test Confirmation model creation."""
    async with async_session_factory() as db:
        from sqlalchemy import select
        result = await db.execute(select(Confirmation))
        confirmations = result.scalars().all()
        assert isinstance(confirmations, list)


@pytest.mark.asyncio
async def test_history_model():
    """Test History model creation."""
    async with async_session_factory() as db:
        from sqlalchemy import select
        result = await db.execute(select(History))
        histories = result.scalars().all()
        assert isinstance(histories, list)


@pytest.mark.asyncio
async def test_access_log_model():
    """Test AccessLog model creation."""
    async with async_session_factory() as db:
        from sqlalchemy import select
        result = await db.execute(select(AccessLog))
        logs = result.scalars().all()
        assert isinstance(logs, list)
