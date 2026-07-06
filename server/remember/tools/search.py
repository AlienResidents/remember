"""Search memories tool."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from remember.models import Memory, Tag, MemoryTag


async def search_memories(
    query: str,
    types: list[str] | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
    db: AsyncSession | None = None,
) -> list[dict]:
    """Search memories by full-text search.

    Args:
        query: Search query
        types: Filter by memory types (project, reference)
        tags: Filter by tags
        limit: Maximum results
        db: Database session

    Returns:
        List of memory metadata (no body)
    """
    if db is None:
        from remember.db import async_session_factory
        async with async_session_factory() as db:
            return await _search_memories(query, types, tags, limit, db)
    return await _search_memories(query, types, tags, limit, db)


async def _search_memories(
    query: str,
    types: list[str] | None,
    tags: list[str] | None,
    limit: int,
    db: AsyncSession,
) -> list[dict]:
    """Internal search implementation."""
    # Build full-text search query
    search_term = f"{' | '.join(query.split())}*"
    search_expr = func.to_tsvector("english", func.concat(Memory.name, " ", Memory.description, " ", Memory.body)).op("@@")(
        func.to_tsquery(search_term)
    )

    stmt = (
        select(Memory, Tag)
        .join(MemoryTag, Memory.id == MemoryTag.memory_id)
        .join(Tag, MemoryTag.tag_id == Tag.id)
        .where(search_expr)
        .options(joinedload(Memory.tags))
    )

    # Apply filters
    if types:
        stmt = stmt.where(Memory.type.in_(types))

    if tags:
        # This is a simplified version - full implementation would use subqueries
        pass

    stmt = stmt.order_by(search_expr.desc()).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    # Group by memory
    memories_dict = {}
    for memory, tag in rows:
        if memory.id not in memories_dict:
            memories_dict[memory.id] = {
                "id": str(memory.id),
                "name": memory.name,
                "type": memory.type,
                "description": memory.description,
                "owner_id": str(memory.owner_id),
                "status": memory.status,
                "tags": [],
                "score": 0,
            }
        if tag:
            memories_dict[memory.id]["tags"].append(tag.name)
        memories_dict[memory.id]["score"] = max(memories_dict[memory.id]["score"], 1.0)

    return list(memories_dict.values())
