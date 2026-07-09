---
type: Source Code
description: "Tests for database connection and session management."
resource: server/tests/test_db.py
timestamp: 2026-07-09T01:43:40Z
---

# test db

Source path: `server/tests/test_db.py`

## Content

```python
"""Tests for database connection and session management."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from remember.db import get_db, init_db, close_db, async_session_factory


@pytest.mark.asyncio
async def test_get_db(db_session: AsyncSession):
    """Test getting a database session."""
    assert db_session is not None
    assert isinstance(db_session, AsyncSession)


@pytest.mark.asyncio
async def test_db_session_isolation(db_session: AsyncSession):
    """Test that database sessions are isolated."""
    from remember.models import User
    import uuid
    from datetime import datetime, timezone

    user = User(
        id=uuid.uuid4(),
        provider="github",
        provider_id="isolation-test",
        display_name="Isolation Test",
        email="isolation@example.com",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()

    # Verify the user was committed
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.provider_id == "isolation-test"))
    users = result.scalars().all()
    assert len(users) == 1
    assert users[0].display_name == "Isolation Test"

```

*…truncated — full source at `server/tests/test_db.py`*
