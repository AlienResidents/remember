"""Test configuration and fixtures."""

import asyncio
import os
import uuid as uuid_module

# M1/M5: Tests run in dev mode so the session-secret fail-hard check
# doesn't abort. In production, dev_mode=False requires SESSION_SECRET.
os.environ.setdefault("REMEMBER_AUTH__DEV_MODE", "true")

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import remember.db
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

    Uses StaticPool so all sessions share the same in-memory database.
    Without this, each new connection gets its own blank :memory: database,
    and tables created by db_session would not be visible to code that
    opens its own session via the global async_session_factory (e.g. auth
    providers).

    Registers a gen_random_uuid() function so PostgreSQL-specific
    server_defaults work under SQLite.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
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

    factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def patch_db(test_engine, db_session):
    """Patch the global remember.db to use the test engine.

    Some code (auth providers, server lifespan) imports
    `async_session_factory` and `engine` directly from `remember.db` at
    module level. Without patching, they connect to the configured
    PostgreSQL database. This fixture swaps the globals to point at the
    in-memory test engine so that code sees the same database as the
    `db_session` fixture.

    Also patches each auth provider module's local `async_session_factory`
    binding — `from remember.db import async_session_factory` at module
    level captures the original factory, so we must replace it in each
    module's namespace.

    Requires `db_session` so tables exist for the duration of the patch.
    """
    import importlib

    factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Patch remember.db globals
    original_engine = remember.db.engine
    original_factory = remember.db.async_session_factory
    remember.db.engine = test_engine
    remember.db.async_session_factory = factory

    # Patch all auth provider modules that bound async_session_factory at import time
    auth_modules = [
        "remember.auth.dev",
        "remember.auth.tailscale",
        "remember.auth.api_key",
        "remember.auth.github",
        "remember.auth.google",
        "remember.auth.microsoft",
        "remember.auth.keycloak",
        "remember.auth.authentik",
        "remember.auth.dex",
    ]
    originals = {}
    for mod_name in auth_modules:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "async_session_factory"):
            originals[mod_name] = mod.async_session_factory
            mod.async_session_factory = factory

    yield

    # Restore
    remember.db.engine = original_engine
    remember.db.async_session_factory = original_factory
    for mod_name, orig_factory in originals.items():
        mod = importlib.import_module(mod_name)
        mod.async_session_factory = orig_factory


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