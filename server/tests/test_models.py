"""Tests for SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import User, Memory, Tag, MemoryTag, Confirmation, MemoryHistory


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession, test_user: User):
    """Test creating a user."""
    assert test_user.id is not None
    assert test_user.provider == "keycloak"
    assert test_user.provider_id == "testuser"
    assert test_user.display_name == "Test User"
    assert test_user.email == "test@example.com"
    assert test_user.created_at is not None


@pytest.mark.asyncio
async def test_create_memory(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test creating a memory."""
    assert test_memory.id is not None
    assert test_memory.name == "test-memory"
    assert test_memory.type == "project"
    assert test_memory.description == "A test memory"
    assert test_memory.body == "# Test Memory\n\nThis is a test."
    assert test_memory.owner_id == test_user.id
    assert test_memory.status == "active"
    assert test_memory.created_at is not None
    assert test_memory.updated_at is not None


@pytest.mark.asyncio
async def test_memory_type_constraint(db_session: AsyncSession, test_user: User):
    """Test that memory type is constrained to project/reference."""
    import uuid

    memory = Memory(
        id=uuid.uuid4(),
        name="invalid-type",
        type="invalid",  # Should fail
        description="Invalid type",
        body="Body",
        owner_id=test_user.id,
    )
    db_session.add(memory)

    with pytest.raises(Exception):  # Should raise integrity error
        await db_session.commit()


@pytest.mark.asyncio
async def test_memory_status_constraint(db_session: AsyncSession, test_user: User):
    """Test that memory status is constrained."""
    import uuid

    memory = Memory(
        id=uuid.uuid4(),
        name="invalid-status",
        type="project",
        description="Invalid status",
        body="Body",
        owner_id=test_user.id,
        status="invalid",  # Should fail
    )
    db_session.add(memory)

    with pytest.raises(Exception):  # Should raise integrity error
        await db_session.commit()


@pytest.mark.asyncio
async def test_unique_owner_name_constraint(db_session: AsyncSession, test_user: User):
    """Test that owner+name is unique."""
    import uuid

    memory1 = Memory(
        id=uuid.uuid4(),
        name="duplicate-name",
        type="project",
        description="First",
        body="Body 1",
        owner_id=test_user.id,
    )
    memory2 = Memory(
        id=uuid.uuid4(),
        name="duplicate-name",  # Same name, same owner
        type="project",
        description="Second",
        body="Body 2",
        owner_id=test_user.id,
    )

    db_session.add(memory1)
    await db_session.commit()

    db_session.add(memory2)
    with pytest.raises(Exception):  # Should raise integrity error
        await db_session.commit()


@pytest.mark.asyncio
async def test_create_tag(db_session: AsyncSession):
    """Test creating a tag."""
    import uuid
    from datetime import datetime, timezone

    tag = Tag(
        id=uuid.uuid4(),
        name="test-tag",
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    assert tag.id is not None
    assert tag.name == "test-tag"


@pytest.mark.asyncio
async def test_memory_tag_relationship(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test memory-tag relationship."""
    import uuid
    from datetime import datetime, timezone

    tag = Tag(id=uuid.uuid4(), name="related-tag")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    memory_tag = MemoryTag(memory_id=test_memory.id, tag_id=tag.id)
    db_session.add(memory_tag)
    await db_session.commit()

    # Refresh memory to load tags — must specify attribute_names for async
    # (lazy loading in async context raises MissingGreenlet without it)
    await db_session.refresh(test_memory, attribute_names=["tags"])
    assert len(test_memory.tags) == 1
    assert test_memory.tags[0].name == "related-tag"


@pytest.mark.asyncio
async def test_confirmation(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test creating a confirmation."""
    import uuid
    from datetime import datetime, timezone

    confirmation = Confirmation(
        memory_id=test_memory.id,
        user_id=test_user.id,
        note="This is accurate",
    )
    db_session.add(confirmation)
    await db_session.commit()
    await db_session.refresh(confirmation)

    assert confirmation.memory_id == test_memory.id
    assert confirmation.user_id == test_user.id
    assert confirmation.note == "This is accurate"
    assert confirmation.confirmed_at is not None


@pytest.mark.asyncio
async def test_memory_history(db_session: AsyncSession, test_user: User, test_memory: Memory):
    """Test creating memory history."""
    import uuid
    from datetime import datetime, timezone

    history = MemoryHistory(
        id=uuid.uuid4(),
        memory_id=test_memory.id,
        body="# Updated body",
        description="Updated description",
        edited_by=test_user.id,
    )
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)

    assert history.memory_id == test_memory.id
    assert history.body == "# Updated body"
    assert history.edited_by == test_user.id
    assert history.edited_at is not None
