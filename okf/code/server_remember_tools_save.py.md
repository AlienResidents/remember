---
type: Source Code
description: "Save memory tool."
resource: server/remember/tools/save.py
timestamp: 2026-07-09T13:54:50Z
---

# save

Source path: `server/remember/tools/save.py`

## Content

```python
"""Save memory tool."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from remember.models import Memory, Tag, MemoryTag, MemoryHistory
from remember.db import async_session_factory


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
) -> dict:
    """Save or update a memory (upsert on owner+name).

    Args:
        name: Memory name (unique per owner)
        type: Memory type (project or reference)
        description: Brief description
        body: Full markdown content
        owner_id: Owner user ID
        tags: List of tag names
        import_source: Source identifier for imports
        preserve_created_at: Preserve original created_at (for imports)
        db: Database session

    Returns:
        Memory ID and confirmation message
    """
```

*…truncated — full source at `server/remember/tools/save.py`*
