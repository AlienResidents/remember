---
type: Source Code
description: "Tests for database migrations."
resource: server/tests/test_migrations.py
timestamp: 2026-07-09T01:43:40Z
---

# test migrations

Source path: `server/tests/test_migrations.py`

## Content

```python
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
```

*…truncated — full source at `server/tests/test_migrations.py`*
