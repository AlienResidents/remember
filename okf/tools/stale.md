---
type: tool
title: Stale
description: Identify memories past verification threshold.
resource: server/remember/tools/stale.py
tags: [stale, verification, threshold]
timestamp: 2026-07-06T00:00:00Z
---

# Stale

## Overview

Returns active memories that haven't been verified within the threshold period. Memories with no `last_verified_at` are always considered stale.

## Function Signature

```python
async def get_stale_memories(
    threshold_days: int = 90,
    limit: int = 50,
    db: AsyncSession | None = None,
) -> list[dict]
```

## Returns

Same as [List](list.md) with additional `last_verified_at` and `age_days` fields.

## Related Concepts

* [Verify](verify.md)
* [Tools Overview](overview.md)
