---
type: Source Code
description: "Search memories tool."
resource: server/remember/tools/search.py
timestamp: 2026-07-10T02:44:34Z
---

# search

Source path: `server/remember/tools/search.py`

## Content

```python
"""Search memories tool."""

import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from remember.models import Memory, Tag, MemoryTag


async def search_memories(
    query: str,
    types: list[str] | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
    owner_id: uuid.UUID | None = None,
    db: AsyncSession | None = None,
) -> list[dict]:
    """Search memories by full-text search.

    Args:
        query: Search query
        types: Filter by memory types (project, reference)
        tags: Filter by tags
        limit: Maximum results
        owner_id: Filter by owner (security: scope to authenticated user)
        db: Database session

    Returns:
        List of memory metadata (no body)
    """
    if db is None:
        from remember.db import async_session_factory
        async with async_session_factory() as db:
            return await _search_memories(query, types, tags, limit, owner_id, db)
    return await _search_memories(query, types, tags, limit, owner_id, db)


async def _search_memories(
```

*…truncated — full source at `server/remember/tools/search.py`*
