"""Vector search tool using pgvector."""

import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from remember.models import Memory
from remember.db import async_session_factory


async def search_memories_vector(
    query_embedding: list[float],
    limit: int = 10,
    threshold: float = 0.5,
    db: AsyncSession | None = None,
) -> list[dict]:
    """Search memories using vector similarity.

    Args:
        query_embedding: Query vector (1536 dimensions for text-embedding-3-small)
        limit: Maximum results
        threshold: Minimum similarity score (0-1)
        db: Database session

    Returns:
        List of memory metadata with similarity scores
    """
    if db is None:
        async with async_session_factory() as db:
            return await _search_memories_vector(query_embedding, limit, threshold, db)
    return await _search_memories_vector(query_embedding, limit, threshold, db)


async def _search_memories_vector(
    query_embedding: list[float],
    limit: int,
    threshold: float,
    db: AsyncSession,
) -> list[dict]:
    """Internal vector search implementation."""
    # Use cosine similarity
    embedding_expr = func.cosine_similarity(Memory.embedding, func.array(query_embedding).cast("vector(1536)"))

    stmt = (
        select(Memory, embedding_expr.label("similarity"))
        .where(Memory.embedding.isnot(None))
        .where(embedding_expr >= threshold)
        .order_by(embedding_expr.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": str(m.id),
            "name": m.name,
            "type": m.type,
            "description": m.description,
            "owner_id": str(m.owner_id),
            "status": m.status,
            "similarity": float(sim),
        }
        for m, sim in rows
    ]
