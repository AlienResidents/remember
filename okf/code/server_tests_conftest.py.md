---
type: Source Code
description: "Test configuration and fixtures."
resource: server/tests/conftest.py
timestamp: 2026-07-10T02:44:34Z
---

# conftest

Source path: `server/tests/conftest.py`

## Content

```python
"""Test configuration and fixtures."""

import asyncio
import uuid as uuid_module

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from remember.db import Base
from remember.models import User, Memory


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine (in-memory SQLite).

    Registers a gen_random_uuid() function so PostgreSQL-specific
    server_defaults work under SQLite.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Register PostgreSQL functions that the models use as server_defaults
    @event.listens_for(engine.sync_engine, "connect")
    def _register_functions(dbapi_conn, _conn_record):
        dbapi_conn.create_function("gen_random_uuid", 0, lambda: str(uuid_module.uuid4()))

    yield engine
```

*…truncated — full source at `server/tests/conftest.py`*
