---
type: model
title: Database Schema
description: Complete PostgreSQL schema with SQLAlchemy models, constraints, and indexes.
resource: server/remember/models.py
tags: [database, schema, postgresql, pgvector]
timestamp: 2026-07-06T00:00:00Z
---

# Database Schema

## Tables

### `users`

Team members identified via auth providers.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK, `gen_random_uuid()` |
| `provider` | TEXT | NOT NULL |
| `provider_id` | TEXT | NOT NULL, indexed |
| `display_name` | TEXT | NOT NULL |
| `email` | TEXT | NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL, `now()` |
| `last_seen_at` | TIMESTAMPTZ | NULL |

### `memories`

Team memories with ownership and status tracking.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK, `gen_random_uuid()` |
| `name` | TEXT | NOT NULL |
| `type` | TEXT | NOT NULL, CHECK `('project', 'reference')` |
| `description` | TEXT | NOT NULL |
| `body` | TEXT | NOT NULL |
| `owner_id` | UUID | FK → `users.id`, NOT NULL |
| `status` | TEXT | NOT NULL, CHECK `('active', 'archived', 'disputed')` |
| `created_at` | TIMESTAMPTZ | NOT NULL, `now()` |
| `updated_at` | TIMESTAMPTZ | NOT NULL, `now()`, onupdate |
| `last_verified_at` | TIMESTAMPTZ | NULL |
| `embedding` | vector(1536) | NULL (pgvector) |
| `import_source` | TEXT | NULL |

**Constraints:**
- UNIQUE `(owner_id, name)`
- INDEX `(owner_id)`, `(type)`, `(updated_at DESC)`, `(status)`
- HNSW index on `embedding` (Phase C)

### `tags`

Categorization tags.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `name` | TEXT | NOT NULL, UNIQUE |

### `memory_tags`

Association table (many-to-many).

| Column | Type | Constraints |
|--------|------|-------------|
| `memory_id` | UUID | PK, FK → `memories.id` CASCADE |
| `tag_id` | UUID | PK, FK → `tags.id` CASCADE |

### `confirmations`

User confirmations/refutations.

| Column | Type | Constraints |
|--------|------|-------------|
| `memory_id` | UUID | PK, FK → `memories.id` CASCADE |
| `user_id` | UUID | PK, FK → `users.id` |
| `confirmed_at` | TIMESTAMPTZ | NOT NULL, `now()` |
| `note` | TEXT | NULL |

### `memory_history`

Append-only edit history.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `memory_id` | UUID | FK → `memories.id` CASCADE |
| `body` | TEXT | NOT NULL |
| `description` | TEXT | NOT NULL |
| `edited_by` | UUID | FK → `users.id` |
| `edited_at` | TIMESTAMPTZ | NOT NULL, `now()` |

### `access_log`

Read tracking (high-volume, uses BIGSERIAL).

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | BIGSERIAL | PK |
| `memory_id` | UUID | FK → `memories.id` CASCADE |
| `read_by` | UUID | FK → `users.id` |
| `accessed_at` | TIMESTAMPTZ | NOT NULL, `now()` |

**Indexes:** `(memory_id)`, `(read_by)`, `(accessed_at)`

## Views

### `stale_memories`

```sql
SELECT m.*, (now() - GREATEST(m.last_verified_at, m.updated_at)) AS age
FROM memories m
WHERE m.status = 'active'
  AND GREATEST(m.last_verified_at, m.updated_at) < now() - interval '90 days';
```

## Related Concepts

* [Server](../server.md)
* [Save Tool](../tools/save.md)
