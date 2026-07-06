---
type: tool
title: Confirm
description: Add confirmation, remove existing refutation from same user.
resource: server/remember/tools/confirm.py
tags: [confirm, community, consensus]
timestamp: 2026-07-06T00:00:00Z
---

# Confirm

## Overview

Adds a confirmation row to `confirmations`. If the same user previously refuted this memory, the refutation is removed.

## Function Signature

```python
async def confirm_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    note: str | None = None,
    db: AsyncSession | None = None,
) -> dict
```

## Behavior

- Any user can confirm
- Removes existing refutation from same user (if any)
- Adds confirmation row

## Returns

```json
{"message": "Memory confirmed successfully"}
```

## Related Concepts

* [Refute](refute.md)
* [Tools Overview](overview.md)
