"""Get stale memories tool."""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory
from remember.db import async_session_factory


async def get_stale_memories(
    threshold_days: int = 90,
    limit: int = 50,
    db: AsyncSession | None = None,
) -> list[dict]:
    """Get memories that haven't been verified recently.

    Args:
        threshold_days: Days before marking as stale
        limit: Maximum results
        db: Database session

    Returns:
        List of stale memories with age information
    """
    if db is None:
        async with async_session_factory() as db:
            return await _get_stale_memories(threshold_days, limit, db)
    return await _get_stale_memories(threshold_days, limit, db)


async def _get_stale_memories(
    threshold_days: int,
    limit: int,
    db: AsyncSession,
) -> list[dict]:
    """Internal stale implementation."""
    threshold = datetime.now(timezone.utc) - timedelta(days=threshold_days)

    stmt = (
        select(Memory)
        .where(Memory.status == "active")
        .where(
            (Memory.last_verified_at < threshold) | (Memory.last_verified_at.is_(None))
        )
        .order_by(Memory.updated_at.asc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    memories = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "name": m.name,
            "type": m.type,
            "description": m.description,
            "owner_id": str(m.owner_id),
            "last_verified_at": str(m.last_verified_at) if m.last_verified_at else None,
            "updated_at": str(m.updated_at),
            "age_days": (datetime.now(timezone.utc) - m.updated_at.replace(tzinfo=timezone.utc)).days,
        }
        for m in memories
    ]
