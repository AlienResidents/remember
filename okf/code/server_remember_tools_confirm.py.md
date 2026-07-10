---
type: Source Code
description: "Confirm memory tool."
resource: server/remember/tools/confirm.py
timestamp: 2026-07-10T02:44:33Z
---

# confirm

Source path: `server/remember/tools/confirm.py`

## Content

```python
"""Confirm memory tool."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory, Confirmation
from remember.db import async_session_factory


async def confirm_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    note: str | None = None,
    db: AsyncSession | None = None,
) -> dict:
    """Confirm a memory (signal agreement).

    Args:
        memory_id: Memory UUID
        user_id: Current user ID
        note: Optional confirmation note
        db: Database session

    Returns:
        Confirmation message
    """
    if db is None:
        async with async_session_factory() as db:
            return await _confirm_memory(memory_id, user_id, note, db)
    return await _confirm_memory(memory_id, user_id, note, db)


async def _confirm_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    note: str | None,
    db: AsyncSession,
) -> dict:
```

*…truncated — full source at `server/remember/tools/confirm.py`*
