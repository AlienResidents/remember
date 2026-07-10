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
    )

    async with async_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    from datetime import datetime, timezone

    user = User(
        id=uuid_module.uuid4(),
        provider="keycloak",
        provider_id="testuser",
        display_name="Test User",
        email="test@example.com",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def second_user(db_session: AsyncSession) -> User:
    """Create a second test user for authorization tests."""
    from datetime import datetime, timezone

    user = User(
        id=uuid_module.uuid4(),
        provider="keycloak",
        provider_id="otheruser",
        display_name="Other User",
        email="other@example.com",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_memory(db_session: AsyncSession, test_user: User) -> Memory:
    """Create a test memory owned by test_user."""
    from datetime import datetime, timezone

    memory = Memory(
        id=uuid_module.uuid4(),
        name="test-memory",
        type="project",
        description="A test memory",
        body="# Test Memory\n\nThis is a test.",
        owner_id=test_user.id,
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(memory)
    await db_session.commit()
    await db_session.refresh(memory)
    return memory