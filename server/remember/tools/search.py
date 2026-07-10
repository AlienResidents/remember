"""Search memories tool."""

import re
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from remember.models import Memory, Tag, MemoryTag


# PostgreSQL to_tsquery operators — if these appear in user input, to_tsquery
# raises a syntax error (unhandled → 500). Strip them before constructing the
# tsquery. We split on whitespace and join with " | " (OR), so the only
# operators we want are the ones WE add, never from user input.
_TSQUERY_OPERATOR_RE = re.compile(r'[!&|():*"\\]')


def _sanitize_tsquery(query: str) -> str:
    """Sanitize user input for safe use in PostgreSQL to_tsquery.

    Strips all tsquery operators (!, &, |, (, ), :, *, double-quote, backslash) from each word so user
    input can never produce a tsquery syntax error. Returns a tsquery string
    of the form "word1 | word2 | word3*" (OR of words, prefix match on last).
    """
    words = [_TSQUERY_OPERATOR_RE.sub("", w) for w in query.split()]
    words = [w for w in words if w]  # drop empty words (e.g. input was all operators)
    if not words:
        return ""
    # OR the words together; append * for prefix matching on the last word only
    return " | ".join(words) + "*"


async def search_memories(
    query: str,
    types: list[str] | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
    owner_id: uuid.UUID | None = None,
    db: AsyncSession | None = None,
) -> list[dict]:
    """Search memories by full-text search.

    Args:
        query: Search query
        types: Filter by memory types (project, reference)
        tags: Filter by tags
        limit: Maximum results
        owner_id: Filter by owner (security: scope to authenticated user)
        db: Database session

    Returns:
        List of memory metadata (no body)
    """
    if db is None:
        from remember.db import async_session_factory
        async with async_session_factory() as db:
            return await _search_memories(query, types, tags, limit, owner_id, db)
    return await _search_memories(query, types, tags, limit, owner_id, db)


async def _search_memories(
    query: str,
    types: list[str] | None,
    tags: list[str] | None,
    limit: int,
    owner_id: uuid.UUID | None,
    db: AsyncSession,
) -> list[dict]:
    """Internal search implementation."""
    # Sanitize user input before constructing the tsquery — PostgreSQL's
    # to_tsquery raises a syntax error on operator chars (! & | ( ) : *).
    search_term = _sanitize_tsquery(query)
    if not search_term:
        # Query was empty after stripping operators — return no results
        # rather than passing an empty tsquery (which also errors).
        return []
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

    # Security: scope to owner if provided
    if owner_id:
        stmt = stmt.where(Memory.owner_id == owner_id)

    # Apply filters
    if types:
        stmt = stmt.where(Memory.type.in_(types))

    if tags:
        # This is a simplified version - full implementation would use subqueries
        pass

    stmt = stmt.order_by(search_expr.desc()).limit(limit)

    result = await db.execute(stmt)
    rows = result.unique().all()

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
