---
type: Source Code
description: "Test configuration and fixtures."
resource: server/tests/conftest.py
timestamp: 2026-07-09T14:09:54Z
---

# conftest

Source path: `server/tests/conftest.py`

## Content

```python
"""Test configuration and fixtures."""

import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from remember.db import Base, get_db
from remember.models import User, Memory


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    yield engine
    asyncio.run(engine.dispose())


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
```

*…truncated — full source at `server/tests/conftest.py`*
