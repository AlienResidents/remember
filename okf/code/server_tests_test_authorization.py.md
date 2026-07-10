---
type: Source Code
description: "Tests for authorization — C2 (per-memory access control)."
resource: server/tests/test_authorization.py
timestamp: 2026-07-10T02:44:34Z
---

# test authorization

Source path: `server/tests/test_authorization.py`

## Content

```python
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
```

*…truncated — full source at `server/tests/test_authorization.py`*
