---
type: Source Code
description: "Verify memory tool."
resource: server/remember/tools/verify.py
timestamp: 2026-07-09T13:05:53Z
---

# verify

Source path: `server/remember/tools/verify.py`

## Content

```python
"""Verify memory tool."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory
from remember.db import async_session_factory


async def verify_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession | None = None,
) -> dict:
    """Verify a memory (bump last_verified_at).

    Args:
        memory_id: Memory UUID
        user_id: Current user ID
        db: Database session

    Returns:
        Confirmation message
    """
    if db is None:
        async with async_session_factory() as db:
            return await _verify_memory(memory_id, user_id, db)
    return await _verify_memory(memory_id, user_id, db)


async def _verify_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    """Internal verify implementation."""
    stmt = select(Memory).where(Memory.id == memory_id)
    result = await db.execute(stmt)
```

*…truncated — full source at `server/remember/tools/verify.py`*
