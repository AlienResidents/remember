---
type: tool
title: Save
description: Upsert memory with history tracking on (owner_id, name).
resource: server/remember/tools/save.py
tags: [save, upsert, history]
timestamp: 2026-07-06T00:00:00Z
---

# Save

## Overview

Creates or updates a memory. On update, the previous version is preserved in `memory_history`. Enforces `type` constraint (`project` or `reference`).

## Function Signature

```python
async def save_memory(
    name: str,
    type: str,
    description: str,
    body: str,
    owner_id: uuid.UUID,
    tags: list[str] | None = None,
    import_source: str | None = None,
    preserve_created_at: datetime | None = None,
    db: AsyncSession | None = None,
) -> dict
```

## Behavior

- **New memory**: Creates row with `status='active'`, `created_at=now()`
- **Existing memory** (same owner+name): Saves current body to `memory_history`, updates in place
- **Tags**: Replaced entirely on update (old associations deleted, new ones created)
- **`preserve_created_at`**: For imports — keeps original creation timestamp

## Returns

```json
{"id": "uuid", "message": "Memory saved successfully"}
```

## Related Concepts

* [Tools Overview](overview.md)
