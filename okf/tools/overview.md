---
type: tool
title: MCP Tools Overview
description: Complete MCP tool surface with signatures, behavior, and ownership rules.
resource: server/remember/tools/
tags: [mcp, tools, api]
timestamp: 2026-07-06T00:00:00Z
---

# MCP Tools Overview

## Read Tools

| Tool | Function | Owner Enforced |
|------|----------|----------------|
| `search_memories(query, types?, tags?, limit=10)` | Full-text search. Returns ranked metadata (no body). | No |
| `get_memory(id, user_id)` | Full memory incl. body, history count, confirmations. Logs access. | No |
| `list_memories(owner?, type?, tag?, status='active', updated_since?)` | Paginated browse. | No |
| `get_stale_memories(threshold_days=90)` | Returns memories older than threshold. | No |

## Write Tools (Owner Enforced)

| Tool | Function | Behavior |
|------|----------|----------|
| `save_memory(name, type, description, body, owner_id, tags?, import_source?, preserve_created_at?)` | Upsert on `(owner_id, name)`. Previous version → history. Rejects `type` outside `{'project', 'reference'}`. | Owner only |
| `verify_memory(memory_id, user_id)` | Bump `last_verified_at`. | Owner only |
| `archive_memory(memory_id, user_id)` | Set `status = 'archived'`. | Owner only |

## Community Tools (Any User)

| Tool | Function | Behavior |
|------|----------|----------|
| `confirm_memory(memory_id, user_id, note?)` | Add confirmation. Removes any existing refutation from same user. | Any user |
| `refute_memory(memory_id, user_id, reason)` | Add refutation. First refutation sets `status = 'disputed'`. Removes any existing confirmation from same user. | Any user |

## Related Concepts

* [Search](search.md)
* [Search Vector](search_vector.md)
* [Save](save.md)
* [Get](get.md)
* [List](list.md)
* [Stale](stale.md)
* [Verify](verify.md)
* [Archive](archive.md)
* [Confirm](confirm.md)
* [Refute](refute.md)
