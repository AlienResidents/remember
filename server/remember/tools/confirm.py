"""Confirm memory tool."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory, Confirmation
from remember.db import async_session_factory


async def confirm_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    note: str | None = None,
    db: AsyncSession | None = None,
) -> dict:
    """Confirm a memory (signal agreement).

    Args:
        memory_id: Memory UUID
        user_id: Current user ID
        note: Optional confirmation note
        db: Database session

    Returns:
        Confirmation message
    """
    if db is None:
        async with async_session_factory() as db:
            return await _confirm_memory(memory_id, user_id, note, db)
    return await _confirm_memory(memory_id, user_id, note, db)


async def _confirm_memory(
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    note: str | None,
    db: AsyncSession,
) -> dict:
    """Internal confirm implementation."""
    # Check if memory exists
    stmt = select(Memory).where(Memory.id == memory_id)
    result = await db.execute(stmt)
    memory = result.scalar_one_or_none()

    if not memory:
        return {"error": "Memory not found"}

    # Remove existing refutation if any
    stmt = select(Confirmation).where(
        Confirmation.memory_id == memory_id,
        Confirmation.user_id == user_id,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing and "refute" in (existing.note or "").lower():
        await db.delete(existing)

    # Add confirmation
    confirmation = Confirmation(
        memory_id=memory_id,
        user_id=user_id,
        note=note,
        confirmed_at=datetime.now(timezone.utc),
    )
    db.add(confirmation)
    await db.commit()

    return {"message": "Memory confirmed successfully"}
