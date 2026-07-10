"""Verify memory tool."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory
from remember.db import async_session_factory


async def verify_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession | None = None,
) -> dict:
    """Verify a memory (bump last_verified_at).

    Args:
        memory_id: Memory UUID
        user_id: Current user ID
        db: Database session

    Returns:
        Confirmation message
    """
    if db is None:
        async with async_session_factory() as db:
            return await _verify_memory(memory_id, user_id, db)
    return await _verify_memory(memory_id, user_id, db)


async def _verify_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    """Internal verify implementation."""
    # L6: Filter by owner_id in the query -- uniform "not found" error for
    # both not-found and not-owned, so non-owners can't probe memory existence.
    stmt = select(Memory).where(Memory.id == memory_id, Memory.owner_id == user_id)
    result = await db.execute(stmt)
    memory = result.scalar_one_or_none()

    if not memory:
        return {"error": "Memory not found"}

    memory.last_verified_at = datetime.now(timezone.utc)
    await db.commit()

    return {"message": "Memory verified successfully"}
