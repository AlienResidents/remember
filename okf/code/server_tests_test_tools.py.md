---
type: Source Code
description: "Tests for MCP tools."
resource: server/tests/test_tools.py
timestamp: 2026-07-09T13:54:50Z
---

# test tools

Source path: `server/tests/test_tools.py`

## Content

```python
"""Tests for MCP tools."""

import uuid
from datetime import datetime, timezone

import pytest
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
```

*…truncated — full source at `server/tests/test_tools.py`*
