---
type: Source Code
description: "Vector search tool using pgvector."
resource: server/remember/tools/search_vector.py
timestamp: 2026-07-09T13:05:53Z
---

# search vector

Source path: `server/remember/tools/search_vector.py`

## Content

```python
"""Vector search tool using pgvector."""

import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory
from remember.db import async_session_factory


async def search_memories_vector(
    query_embedding: list[float],
    limit: int = 10,
    threshold: float = 0.5,
    db: AsyncSession | None = None,
) -> list[dict]:
    """Search memories using vector similarity.

    Args:
        query_embedding: Query vector (1536 dimensions for text-embedding-3-small)
        limit: Maximum results
        threshold: Minimum similarity score (0-1)
        db: Database session

    Returns:
        List of memory metadata with similarity scores
    """
    if db is None:
        async with async_session_factory() as db:
            return await _search_memories_vector(query_embedding, limit, threshold, db)
    return await _search_memories_vector(query_embedding, limit, threshold, db)


async def _search_memories_vector(
    query_embedding: list[float],
    limit: int,
    threshold: float,
    db: AsyncSession,
) -> list[dict]:
    """Internal vector search implementation."""
```

*…truncated — full source at `server/remember/tools/search_vector.py`*
