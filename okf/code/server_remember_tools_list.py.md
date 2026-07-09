---
type: Source Code
description: "List memories tool."
resource: server/remember/tools/list.py
timestamp: 2026-07-09T13:54:50Z
---

# list

Source path: `server/remember/tools/list.py`

## Content

```python
"""List memories tool."""

import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory, Tag, MemoryTag
from remember.db import async_session_factory


async def list_memories(
    owner_id: uuid.UUID | None = None,
    type: str | None = None,
    tag: str | None = None,
    status: str = "active",
    updated_since: datetime | None = None,
    limit: int = 50,
    db: AsyncSession | None = None,
) -> list[dict]:
    """List memories with filters.

    Args:
        owner_id: Filter by owner
        type: Filter by type (project, reference)
        tag: Filter by tag name
        status: Filter by status (active, archived, disputed)
        updated_since: Filter by last updated date
        limit: Maximum results
        db: Database session

    Returns:
        List of memory metadata (no body)
    """
    if db is None:
        async with async_session_factory() as db:
            return await _list_memories(owner_id, type, tag, status, updated_since, limit, db)
    return await _list_memories(owner_id, type, tag, status, updated_since, limit, db)


```

*…truncated — full source at `server/remember/tools/list.py`*
