---
type: Source Code
description: "Refute memory tool."
resource: server/remember/tools/refute.py
timestamp: 2026-07-09T13:05:53Z
---

# refute

Source path: `server/remember/tools/refute.py`

## Content

```python
"""Refute memory tool."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory, Confirmation
from remember.db import async_session_factory


async def refute_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    reason: str,
    db: AsyncSession | None = None,
) -> dict:
    """Refute a memory (signal disagreement).

    Args:
        memory_id: Memory UUID
        user_id: Current user ID
        reason: Explanation of disagreement
        db: Database session

    Returns:
        Confirmation message
    """
    if db is None:
        async with async_session_factory() as db:
            return await _refute_memory(memory_id, user_id, reason, db)
    return await _refute_memory(memory_id, user_id, reason, db)


async def _refute_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    reason: str,
    db: AsyncSession,
) -> dict:
```

*…truncated — full source at `server/remember/tools/refute.py`*
