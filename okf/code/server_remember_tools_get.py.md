---
type: Source Code
description: "Get memory tool."
resource: server/remember/tools/get.py
timestamp: 2026-07-09T13:05:53Z
---

# get

Source path: `server/remember/tools/get.py`

## Content

```python
"""Get memory tool."""

import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from remember.models import Memory, Confirmation, AccessLog
from remember.db import async_session_factory


async def get_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession | None = None,
) -> dict | None:
    """Get a memory by ID with full details.

    Args:
        memory_id: Memory UUID
        user_id: Current user ID (for access logging)
        db: Database session

    Returns:
        Memory with body, history count, confirmations, etc.
    """
    if db is None:
        async with async_session_factory() as db:
            return await _get_memory(memory_id, user_id, db)
    return await _get_memory(memory_id, user_id, db)


async def _get_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict | None:
    """Internal get implementation."""
    # Load memory with relationships
    stmt = (
```

*…truncated — full source at `server/remember/tools/get.py`*
