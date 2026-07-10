---
type: Source Code
description: "Get stale memories tool."
resource: server/remember/tools/stale.py
timestamp: 2026-07-10T02:44:34Z
---

# stale

Source path: `server/remember/tools/stale.py`

## Content

```python
"""Get stale memories tool."""

import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory
from remember.db import async_session_factory


async def get_stale_memories(
    threshold_days: int = 90,
    limit: int = 50,
    owner_id: uuid.UUID | None = None,
    db: AsyncSession | None = None,
) -> list[dict]:
    """Get memories that haven't been verified recently.

    Args:
        threshold_days: Days before marking as stale
        limit: Maximum results
        owner_id: Filter by owner (security: scope to authenticated user)
        db: Database session

    Returns:
        List of stale memories with age information
    """
    if db is None:
        async with async_session_factory() as db:
            return await _get_stale_memories(threshold_days, limit, owner_id, db)
    return await _get_stale_memories(threshold_days, limit, owner_id, db)


async def _get_stale_memories(
    threshold_days: int,
    limit: int,
    owner_id: uuid.UUID | None,
    db: AsyncSession,
) -> list[dict]:
```

*…truncated — full source at `server/remember/tools/stale.py`*
