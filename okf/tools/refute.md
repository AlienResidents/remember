---
type: tool
title: Refute
description: Add refutation, mark disputed on first refutation.
resource: server/remember/tools/refute.py
tags: [refute, community, disputed]
timestamp: 2026-07-06T00:00:00Z
---

# Refute

## Overview

Adds a refutation row to `confirmations`. The first refutation sets `status = 'disputed'`. Removes any existing confirmation from the same user.

## Function Signature

```python
async def refute_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    reason: str,
    db: AsyncSession | None = None,
) -> dict
```

## Behavior

- Any user can refute
- Removes existing confirmation from same user (if any)
- Adds refutation row with `note="Refuted: {reason}"`
- On first refutation: sets `memory.status = 'disputed'`

## Returns

```json
{"message": "Memory refuted successfully"}
```

## Related Concepts

* [Confirm](confirm.md)
* [Tools Overview](overview.md)
