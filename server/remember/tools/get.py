"""Get memory tool."""

import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from remember.models import Memory, Confirmation, AccessLog
from remember.db import async_session_factory


async def get_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession | None = None,
) -> dict | None:
    """Get a memory by ID with full details.

    Args:
        memory_id: Memory UUID
        user_id: Current user ID (for access logging)
        db: Database session

    Returns:
        Memory with body, history count, confirmations, etc.
    """
    if db is None:
        async with async_session_factory() as db:
            return await _get_memory(memory_id, user_id, db)
    return await _get_memory(memory_id, user_id, db)


async def _get_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict | None:
    """Internal get implementation."""
    # Load memory with relationships
    stmt = (
        select(Memory)
        .where(Memory.id == memory_id)
        .options(
            selectinload(Memory.tags),
            selectinload(Memory.confirmations),
            selectinload(Memory.history),
        )
    )
    result = await db.execute(stmt)
    memory = result.scalar_one_or_none()

    if not memory:
        return None

    # Security: only the owner can read full memory details
    if memory.owner_id != user_id:
        return None

    # Log access
    access_log = AccessLog(
        memory_id=memory_id,
        read_by=user_id,
    )
    db.add(access_log)

    # Count confirmations and refutations
    confirmation_count = len(memory.confirmations)
    refutation_count = sum(1 for c in memory.confirmations if c.note and "refute" in c.note.lower())

    return {
        "id": str(memory.id),
        "name": memory.name,
        "type": memory.type,
        "description": memory.description,
        "body": memory.body,
        "owner_id": str(memory.owner_id),
        "status": memory.status,
        "tags": [tag.name for tag in memory.tags],
        "confirmation_count": confirmation_count,
        "refutation_count": refutation_count,
        "history_count": len(memory.history),
        "last_verified_at": str(memory.last_verified_at) if memory.last_verified_at else None,
        "created_at": str(memory.created_at),
        "updated_at": str(memory.updated_at),
    }
