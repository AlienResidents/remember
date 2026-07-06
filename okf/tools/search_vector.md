---
type: tool
title: Search Vector
description: Semantic search using pgvector with cosine similarity.
resource: server/remember/tools/search_vector.py
tags: [search, vector, pgvector, semantic]
timestamp: 2026-07-06T00:00:00Z
---

# Search Vector

## Overview

Semantic search using pgvector `vector(1536)` columns with cosine similarity. Requires embeddings to be populated (e.g., via `text-embedding-3-small`).

## Function Signature

```python
async def search_memories_vector(
    query_embedding: list[float],
    limit: int = 10,
    threshold: float = 0.5,
    db: AsyncSession | None = None,
) -> list[dict]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query_embedding` | `list[float]` | Required | Query vector (1536 dimensions) |
| `limit` | `int` | `10` | Maximum results |
| `threshold` | `float` | `0.5` | Minimum similarity (0-1) |

## Returns

Same format as [Search](search.md) with additional `similarity` field.

## Related Concepts

* [Search](search.md)
* [Tools Overview](overview.md)
