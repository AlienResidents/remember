---
type: tool
title: List
description: Paginated memory listing with filters.
resource: server/remember/tools/list.py
tags: [list, browse, filter]
timestamp: 2026-07-06T00:00:00Z
---

# List

## Overview

Lists memories with optional filters. Returns metadata only (no body). Ordered by `updated_at DESC`.

## Function Signature

```python
async def list_memories(
    owner_id: uuid.UUID | None = None,
    type: str | None = None,
    tag: str | None = None,
    status: str = "active",
    updated_since: datetime | None = None,
    limit: int = 50,
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
    "description": "...",
    "owner_id": "uuid",
    "status": "active|archived|disputed",
    "updated_at": "..."
  }
]
```

## Related Concepts

* [Tools Overview](overview.md)
