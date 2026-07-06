# REMEMBER — Team Memory System

**Recursive Enhanced Memory by Enhanced Recall**

A shared, team-scoped memory store for developer sessions. Extends per-user memory patterns into a team-wide pool, so that one developer's learnings become automatically available to every other developer's session.

## Overview

REMEMBER provides a shared memory layer that allows teams to:
- Store and retrieve collective knowledge
- Maintain context across sessions and projects
- Share insights and learnings across the team
- Build a persistent organizational memory

## Architecture

### Components

```
Developer workstations                    Kubernetes Cluster
┌─────────────────────┐              ┌──────────────────────────┐
│ AI Assistant        │              │ namespace: remember      │
│  + memory plugin    │              │                          │
│  + CLI tool         │──MCP/HTTPS──▶│  ┌────────────────────┐  │
└─────────────────────┘              │  │ remember-server    │  │
                                     │  │ (FastMCP, Python)  │  │
                                     │  │ N replicas, stateless│  │
                                     │  └─────────┬──────────┘  │
                                     │            │ SQL         │
                                     │            ▼             │
                                     │  ┌────────────────────┐  │
                                     │  │ remember-db        │  │
                                     │  │ Postgres + pgvector│  │
                                     │  │ (managed or self)  │  │
                                     │  └────────────────────┘  │
                                     └──────────────────────────┘
```

1. **`remember-server`** — FastMCP (Python) server, stateless, horizontally scalable. Reads identity from configured provider (OAuth, Tailscale, API key, etc.), maps to a `users` row, enforces ownership on writes.

2. **`remember-db`** — Postgres cluster with pgvector extension. Can be managed (RDS, CNPG) or self-hosted.

3. **Web UI** — Sci-fi themed interface for browsing and managing memories without an AI assistant.

4. **`remember` CLI** — local tool for developers. Import/export memories, manage tags, verify stale entries.

## Goals

- **Onboarding acceleration**: new developers benefit from existing team knowledge from day one
- **Knowledge capture with low friction**: team-scoped memories are created as a side effect of normal workflow
- **Ownership-based truth**: the developer whose session saved a memory owns it; others can confirm or refute but not overwrite
- **Staleness surfacing**: memories degrade over time; the system surfaces candidates for re-verification or archival
- **Future-ready**: data model supports Phase C (embeddings-based semantic search and hybrid RAG) without migration

## Non-goals (Phase 1)

- Cross-organization sharing or per-memory ACLs. One team, one scope.
- Multi-cluster or multi-region deployment.
- Rate limiting, quotas, or abuse prevention.
- Raw Slack/Jira/git ingestion. That's Phase C.
- Cross-organization sharing or per-memory ACLs. One team, one scope.
- Multi-cluster or multi-region deployment.
- Rate limiting, quotas, or abuse prevention.
- Raw Slack/Jira/git ingestion. That's Phase C.

## Architecture Decisions

### Stateless server

The server maintains no local state. All state lives in Postgres. This enables:
- Horizontal scaling (add replicas as needed)
- Zero-downtime deployments (RollingUpdate)
- Simple disaster recovery (restore from DB backup)

### Identity providers

Support multiple identity providers via a pluggable auth layer:

**Implemented:**
- GitHub OAuth
- Google OAuth
- Microsoft/Entra ID
- Tailscale identity
- API keys (for CI/CD and automation)
- Keycloak
- Authentik
- Dex
- Local/dev mode (skip auth for development)

### Database migrations

Schema changes use Alembic for Python. Migrations are version-controlled and applied automatically on server startup. This ensures:
- Schema changes are reproducible
- Rollbacks are possible
- Multi-environment consistency

## Data Model

Schema: Postgres + pgvector.

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider      TEXT NOT NULL,              -- 'github', 'tailscale', 'api_key', etc.
    provider_id   TEXT NOT NULL,              -- username, tailnet_user, etc.
    display_name  TEXT NOT NULL,
    email         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at  TIMESTAMPTZ
);

CREATE TABLE memories (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name             TEXT NOT NULL,
    type             TEXT NOT NULL CHECK (type IN ('project', 'reference')),
    description      TEXT NOT NULL,
    body             TEXT NOT NULL,
    owner_id         UUID NOT NULL REFERENCES users(id),
    status           TEXT NOT NULL DEFAULT 'active'
                     CHECK (status IN ('active', 'archived', 'disputed')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_verified_at TIMESTAMPTZ,
    embedding        vector(1536),
    import_source    TEXT,
    UNIQUE (owner_id, name)
);

CREATE TABLE tags (
    id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name  TEXT UNIQUE NOT NULL
);

CREATE TABLE memory_tags (
    memory_id UUID REFERENCES memories(id) ON DELETE CASCADE,
    tag_id    UUID REFERENCES tags(id)     ON DELETE CASCADE,
    PRIMARY KEY (memory_id, tag_id)
);

CREATE TABLE confirmations (
    memory_id    UUID REFERENCES memories(id) ON DELETE CASCADE,
    user_id      UUID REFERENCES users(id),
    confirmed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    note         TEXT,
    PRIMARY KEY (memory_id, user_id)
);

CREATE TABLE memory_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id   UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    body        TEXT NOT NULL,
    description TEXT NOT NULL,
    edited_by   UUID NOT NULL REFERENCES users(id),
    edited_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE access_log (
    id          BIGSERIAL PRIMARY KEY,
    memory_id   UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    read_by     UUID NOT NULL REFERENCES users(id),
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE VIEW stale_memories AS
SELECT m.*, (now() - GREATEST(m.last_verified_at, m.updated_at)) AS age
FROM memories m
WHERE m.status = 'active'
  AND GREATEST(m.last_verified_at, m.updated_at) < now() - interval '90 days';
```

Indexes:

- `GIN (to_tsvector('english', name || ' ' || description || ' ' || body))` — full-text search
- `HNSW (embedding vector_cosine_ops) WHERE embedding IS NOT NULL` — semantic search (Phase C)
- `(owner_id)`, `(type)`, `(updated_at DESC)`, `(status)`

### Key design choices

- **`type` restricted to `project` and `reference`**. `user` and `feedback` memories are inherently personal and do not belong in the team pool.
- **`owner_id` is FK to `users`**. Users are real rows, enabling clean ownership transfer and "who is on the team" queries.
- **`memory_history` is append-only**. History queries are rare; keeps the hot table small.
- **`access_log` uses `BIGSERIAL`**. High-volume writes; cheaper than UUID.
- **Staleness as a view, not extra columns**. Easy to tune the threshold without schema changes.
- **`import_source`** records the provenance of bulk-imported memories for forensics.

## Configuration

All configuration is via environment variables (prefixed with `REMEMBER_`) or YAML config files.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REMEMBER_DATABASE_URL` | Postgres connection string | `postgresql+asyncpg://localhost:5432/remember` |
| `REMEMBER_SERVER_HOST` | Bind address | `0.0.0.0` |
| `REMEMBER_SERVER_PORT` | Bind port | `8000` |
| `REMEMBER_SERVER_WORKERS` | Number of workers | `2` |
| `REMEMBER_AUTH_DEV_MODE` | Enable dev auth (skip auth) | `false` |
| `REMEMBER_SEARCH_TYPE` | Search type (fulltext/hybrid) | `fulltext` |
| `REMEMBER_SEARCH_DEFAULT_LIMIT` | Default search limit | `10` |
| `REMEMBER_STALENESS_THRESHOLD_DAYS` | Days before marking as stale | `90` |

### YAML Config

See [config.example.yaml](../../server/config.example.yaml) for the full YAML format.

## Deployment

### Container images

- `remember-server:latest` — FastMCP server
- `remember-db:latest` — Postgres + pgvector (optional, can use managed service)

### Kubernetes

Helm chart provided for easy installation:

```bash
# See docs/deployment.md for full instructions
helm install remember remember/remember -f my-values.yaml
```

### Local development

```bash
cd server

# Using Podman
podman build -f Containerfile -t remember-server:latest .
podman run -p 8000:8000 -e REMEMBER_AUTH_DEV_MODE=true remember-server:latest

# Using Docker
docker build -f Dockerfile -t remember-server:latest .
docker run -p 8000:8000 -e REMEMBER_AUTH_DEV_MODE=true remember-server:latest
```

## MCP Tool Surface

All tools enforce identity-based caller authentication. Write tools enforce ownership.

### Read tools

| Tool | Function | Purpose |
|------|----------|---------|
| `search_memories(query, types?, tags?, limit=10)` | `search_memories` | Full-text search. Returns ranked metadata (no body). |
| `get_memory(id, user_id)` | `get_memory` | Full memory incl. body, history count, confirmations. Logs access. |
| `list_memories(owner?, type?, tag?, status='active', updated_since?)` | `list_memories` | Paginated browse. |
| `get_stale_memories(threshold_days=90)` | `get_stale_memories` | Returns memories older than threshold. |

### Write tools (owner-enforced)

| Tool | Function | Purpose |
|------|----------|---------|
| `save_memory(name, type, description, body, owner_id, tags?, import_source?, preserve_created_at?)` | `save_memory` | Upsert on `(owner_id, name)`. Previous version → history. Rejects `type` outside `{'project', 'reference'}` at the tool boundary. |
| `verify_memory(memory_id, user_id)` | `verify_memory` | Bump `last_verified_at` without editing body. Owner only. |
| `archive_memory(memory_id, user_id)` | `archive_memory` | Set `status = 'archived'`. Owner only. |

### Community tools (any user)

| Tool | Function | Purpose |
|------|----------|---------|
| `confirm_memory(memory_id, user_id, note?)` | `confirm_memory` | Add a confirmation row. Removes any existing refutation from the same user. |
| `refute_memory(memory_id, user_id, reason)` | `refute_memory` | Add a refutation. First refutation sets `status = 'disputed'`. Removes any existing confirmation from the same user. |

## Phases

### Phase 1 ✅
- [x] Server skeleton (FastMCP + DB schema)
- [x] GitHub OAuth + API keys + dev mode
- [x] Podman containerization
- [x] Basic K8s manifests (Deployment, Service, Ingress, HPA, PDB)
- [x] Alembic migrations
- [x] Tests

### Phase 2 ✅
- [x] Helm chart
- [x] Ingress/TLS
- [x] Auto-scaling
- [x] Prometheus metrics
- [x] Additional auth providers (Tailscale, Google, Microsoft)
- [x] pgvector semantic search
- [x] CLI tool (import/export)

### Phase 3 ✅
- [x] Self-hosted IdP support (Keycloak, Authentik, Dex)
- [x] Web UI (sci-fi themed)
- [x] FastAPI REST API

### Phase 4 (Future)
- [ ] Hybrid RAG system
- [ ] Slack/Teams notifications
- [ ] Multi-cluster deployment
- [ ] Advanced ACLs
- [ ] Memory-to-memory relationships
- [ ] Automated knowledge extraction from git/Slack/Jira

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
