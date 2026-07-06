---
type: tool
title: Search
description: Full-text search using PostgreSQL `to_tsvector`/`to_tsquery`.
resource: server/remember/tools/search.py
tags: [search, fulltext, postgresql]
timestamp: 2026-07-06T00:00:00Z
---

# Search

## Overview

Full-text search using PostgreSQL `to_tsvector('english', ...)` against `name`, `description`, and `body` fields. Returns ranked metadata (no body).

## Function Signature

```python
async def search_memories(
    query: str,
    types: list[str] | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
    db: AsyncSession | None = None,
) -> list[dict]
```

## Returns

```json
[
  {
    "id": "uuid",
    "name": "memory-name",
    "type": "project|reference",
    "description": "Brief description",
    "owner_id": "uuid",
    "status": "active|archived|disputed",
    "tags": ["tag1", "tag2"],
    "score": 0.95
  }
]
```

## Related Concepts

* [Search Vector](search_vector.md)
* [Tools Overview](overview.md)
