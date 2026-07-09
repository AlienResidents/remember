---
type: Source Code
description: "Tests for SQLAlchemy models."
resource: server/tests/test_models.py
timestamp: 2026-07-09T01:43:40Z
---

# test models

Source path: `server/tests/test_models.py`

## Content

```python
"""Tests for SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import User, Memory, Tag, MemoryTag, Confirmation, MemoryHistory


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession, test_user: User):
    """Test creating a user."""
    assert test_user.id is not None
    assert test_user.provider == "github"
    assert test_user.provider_id == "testuser"
    assert test_user.display_name == "Test User"
    assert test_user.email == "test@example.com"
    assert test_user.created_at is not None


@pytest.mark.asyncio
async def test_create_memory(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test creating a memory."""
    assert test_memory.id is not None
    assert test_memory.name == "test-memory"
    assert test_memory.type == "project"
    assert test_memory.description == "A test memory"
    assert test_memory.body == "# Test Memory\n\nThis is a test."
    assert test_memory.owner_id == test_user.id
    assert test_memory.status == "active"
    assert test_memory.created_at is not None
    assert test_memory.updated_at is not None


@pytest.mark.asyncio
async def test_memory_type_constraint(db_session: AsyncSession, test_user: User):
    """Test that memory type is constrained to project/reference."""
    import uuid
```

*…truncated — full source at `server/tests/test_models.py`*
