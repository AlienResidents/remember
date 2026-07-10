---
type: Source Code
description: "Tests for security fixes — L6 (uniform error), L8 (limit cap), L3 (race condition)."
resource: server/tests/test_server_security.py
timestamp: 2026-07-10T16:49:20Z
---

# test server security

Source path: `server/tests/test_server_security.py`

## Content

```python
"""Tests for security fixes — L6 (uniform error), L8 (limit cap), L3 (race condition).

Covers findings from the independent security review:
- L6: confirm/refute/verify/archive return uniform error for not-found and not-owned
- L8: list_memories caps limit to prevent unbounded queries
- L3: get_or_create_user_by_provider_id handles concurrent creation race
"""

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import User, Memory
from remember.tools import (
    confirm_memory,
    refute_memory,
    verify_memory,
    archive_memory,
    list_memories,
    save_memory,
)


# ---------------------------------------------------------------------------
# L6: Uniform error for not-found vs not-owned
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_confirm_non_owner_gets_same_error_as_not_found(
    db_session: AsyncSession, second_user: User, test_memory: Memory
):
    """L6: confirm_memory returns same error for non-owner as for non-existent memory."""
    # Non-existent memory
    result_not_found = await confirm_memory(
        memory_id=uuid.uuid4(),
        user_id=second_user.id,
```

*…truncated — full source at `server/tests/test_server_security.py`*
