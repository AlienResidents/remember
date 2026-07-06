"""List memories tool."""

import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory, Tag, MemoryTag
from remember.db import async_session_factory


async def list_memories(
    owner_id: uuid.UUID | None = None,
    type: str | None = None,
    tag: str | None = None,
    status: str = "active",
    updated_since: datetime | None = None,
    limit: int = 50,
    db: AsyncSession | None = None,
) -> list[dict]:
    """List memories with filters.

    Args:
        owner_id: Filter by owner
        type: Filter by type (project, reference)
        tag: Filter by tag name
        status: Filter by status (active, archived, disputed)
        updated_since: Filter by last updated date
        limit: Maximum results
        db: Database session

    Returns:
        List of memory metadata (no body)
    """
    if db is None:
        async with async_session_factory() as db:
            return await _list_memories(owner_id, type, tag, status, updated_since, limit, db)
    return await _list_memories(owner_id, type, tag, status, updated_since, limit, db)


async def _list_memories(
    owner_id: uuid.UUID | None,
    type: str | None,
    tag: str | None,
    status: str,
    updated_since: datetime | None,
    limit: int,
    db: AsyncSession,
) -> list[dict]:
    """Internal list implementation."""
    stmt = select(Memory)

    # Apply filters
    if owner_id:
        stmt = stmt.where(Memory.owner_id == owner_id)
    if type:
        stmt = stmt.where(Memory.type == type)
    if status:
        stmt = stmt.where(Memory.status == status)
    if updated_since:
        stmt = stmt.where(Memory.updated_at >= updated_since)

    # Join with tags for filtering
    if tag:
        stmt = (
            stmt
            .join(MemoryTag, Memory.id == MemoryTag.memory_id)
            .join(Tag, MemoryTag.tag_id == Tag.id)
            .where(Tag.name == tag)
        )

    stmt = stmt.order_by(Memory.updated_at.desc()).limit(limit)

    result = await db.execute(stmt)
    memories = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "name": m.name,
            "type": m.type,
            "description": m.description,
            "owner_id": str(m.owner_id),
            "status": m.status,
            "updated_at": str(m.updated_at),
        }
        for m in memories
    ]
