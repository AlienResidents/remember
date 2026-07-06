---
type: tool
title: Get
description: Retrieve full memory with relationships and access logging.
resource: server/remember/tools/get.py
tags: [get, retrieve, access-log]
timestamp: 2026-07-06T00:00:00Z
---

# Get

## Overview

Retrieves a memory by ID with all relationships (tags, confirmations, history). Logs the access in `access_log`.

## Function Signature

```python
async def get_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession | None = None,
) -> dict | None
```

## Returns

```json
{
  "id": "uuid",
  "name": "memory-name",
  "type": "project|reference",
  "description": "...",
  "body": "# Full markdown content",
  "owner_id": "uuid",
  "status": "active|archived|disputed",
  "tags": ["tag1"],
  "confirmation_count": 3,
  "refutation_count": 0,
  "history_count": 2,
  "last_verified_at": "2026-07-01T00:00:00Z",
  "created_at": "...",
  "updated_at": "..."
}
```

## Related Concepts

* [Tools Overview](overview.md)
