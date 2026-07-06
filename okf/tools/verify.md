---
type: tool
title: Verify
description: Bump last_verified_at timestamp (owner only).
resource: server/remember/tools/verify.py
tags: [verify, ownership, stale]
timestamp: 2026-07-06T00:00:00Z
---

# Verify

## Overview

Updates `last_verified_at` to now. Only the memory owner can verify. Does not modify body or description.

## Function Signature

```python
async def verify_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession | None = None,
) -> dict
```

## Behavior

- Checks `memory.owner_id == user_id`
- Sets `last_verified_at = now()`
- Returns error if not owner

## Returns

```json
{"message": "Memory verified successfully"}
```

## Related Concepts

* [Stale](stale.md)
* [Tools Overview](overview.md)
