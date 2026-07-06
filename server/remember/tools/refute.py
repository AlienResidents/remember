"""Refute memory tool."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory, Confirmation
from remember.db import async_session_factory


async def refute_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    reason: str,
    db: AsyncSession | None = None,
) -> dict:
    """Refute a memory (signal disagreement).

    Args:
        memory_id: Memory UUID
        user_id: Current user ID
        reason: Explanation of disagreement
        db: Database session

    Returns:
        Confirmation message
    """
    if db is None:
        async with async_session_factory() as db:
            return await _refute_memory(memory_id, user_id, reason, db)
    return await _refute_memory(memory_id, user_id, reason, db)


async def _refute_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    reason: str,
    db: AsyncSession,
) -> dict:
    """Internal refute implementation."""
    # Check if memory exists
    stmt = select(Memory).where(Memory.id == memory_id)
    result = await db.execute(stmt)
    memory = result.scalar_one_or_none()

    if not memory:
        return {"error": "Memory not found"}

    # Remove existing confirmation if any
    stmt = select(Confirmation).where(
        Confirmation.memory_id == memory_id,
        Confirmation.user_id == user_id,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing and "refute" not in (existing.note or "").lower():
        await db.delete(existing)

    # Add refutation
    confirmation = Confirmation(
        memory_id=memory_id,
        user_id=user_id,
        note=f"Refuted: {reason}",
        confirmed_at=datetime.now(timezone.utc),
    )
    db.add(confirmation)

    # Check if this is the first refutation
    stmt = select(Confirmation).where(
        Confirmation.memory_id == memory_id,
        Confirmation.note.like("%Refuted:%"),
    )
    result = await db.execute(stmt)
    refutations = result.scalars().all()

    if len(refutations) == 1:
        # First refutation - mark as disputed
        memory.status = "disputed"

    await db.commit()

    return {"message": "Memory refuted successfully"}
