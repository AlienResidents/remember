---
type: tool
title: Archive
description: Set memory status to archived (owner only).
resource: server/remember/tools/archive.py
tags: [archive, ownership, status]
timestamp: 2026-07-06T00:00:00Z
---

# Archive

## Overview

Sets `status = 'archived'`. Only the memory owner can archive. Archived memories are excluded from default search/list results.

## Function Signature

```python
async def archive_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession | None = None,
) -> dict
```

## Behavior

- Checks `memory.owner_id == user_id`
- Sets `status = 'archived'`
- Returns error if not owner

## Returns

```json
{"message": "Memory archived successfully"}
```

## Related Concepts

* [Tools Overview](overview.md)
