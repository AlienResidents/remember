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
    if db is None:
        async with async_session_factory() as db:
            return await _save_memory(name, type, description, body, owner_id, tags, import_source, preserve_created_at, db)
    return await _save_memory(name, type, description, body, owner_id, tags, import_source, preserve_created_at, db)


async def _save_memory(
    name: str,
    type: str,
    description: str,
    body: str,
    owner_id: uuid.UUID,
    tags: list[str] | None,
    import_source: str | None,
    preserve_created_at: datetime | None,
    db: AsyncSession,
) -> dict:
    """Internal save implementation."""
    # Check if memory exists
    stmt = select(Memory).where(Memory.owner_id == owner_id, Memory.name == name)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing memory
        # Save old version to history
        history = MemoryHistory(
            memory_id=existing.id,
            body=existing.body,
            description=existing.description,
            edited_by=owner_id,
        )
        db.add(history)

        # Update memory
        existing.body = body
        existing.description = description
        existing.updated_at = datetime.now(timezone.utc)
        if import_source:
            existing.import_source = import_source
    else:
        # Create new memory
        created_at = preserve_created_at or datetime.now(timezone.utc)
        existing = Memory(
            id=uuid.uuid4(),
            name=name,
            type=type,
            description=description,
            body=body,
            owner_id=owner_id,
            status="active",
            created_at=created_at,
            updated_at=datetime.now(timezone.utc),
            import_source=import_source,
        )
        db.add(existing)

    # Handle tags
    if tags:
        # Clear existing tags
        stmt = select(MemoryTag).where(MemoryTag.memory_id == existing.id)
        result = await db.execute(stmt)
        old_tags = result.scalars().all()
        for tag in old_tags:
            await db.delete(tag)

        # Add new tags
        for tag_name in tags:
            stmt = select(Tag).where(Tag.name == tag_name)
            result = await db.execute(stmt)
            tag = result.scalar_one_or_none()

            if not tag:
                tag = Tag(id=uuid.uuid4(), name=tag_name)
                db.add(tag)
                await db.flush()

            memory_tag = MemoryTag(memory_id=existing.id, tag_id=tag.id)
            db.add(memory_tag)

    await db.commit()
    await db.refresh(existing)

    return {
        "id": str(existing.id),
        "message": "Memory saved successfully",
    }
