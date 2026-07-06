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

3. **Memory policy plugin** — Integration layer for AI assistants (Claude Code, etc.) that teaches the policy: which memory types are team-scoped, when to proactively search, how to cite ownership.

4. **`remember` CLI** — local tool for developers. Import/export memories, manage tags, verify stale entries.

## Goals

- **Onboarding acceleration**: new developers benefit from existing team knowledge from day one
- **Knowledge capture with low friction**: team-scoped memories are created as a side effect of normal workflow
- **Ownership-based truth**: the developer whose session saved a memory owns it; others can confirm or refute but not overwrite
- **Staleness surfacing**: memories degrade over time; the system surfaces candidates for re-verification or archival
- **Future-ready**: data model supports Phase C (embeddings-based semantic search and hybrid RAG) without migration

## Non-goals (Phase 1)

- Non-assistant clients (web UI). Team uses AI assistants today.
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

**Phase 1 (MVP):**
- GitHub OAuth
- API keys (for CI/CD and automation)
- Local/dev mode (skip auth for development)

**Phase 2 (later):**
- Tailscale identity
- Google OAuth
- Microsoft/Entra ID

**Phase 3 (self-hosted):**
- Keycloak
- Authentik
- oauth2_proxy
- Dex

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

All configuration is via environment variables or config files:

```yaml
# config.yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 2
  
auth:
  providers:
    - type: github
      client_id: "${GITHUB_CLIENT_ID}"
      client_secret: "${GITHUB_CLIENT_SECRET}"
    - type: api_key
      enabled: true
    - type: dev
      enabled: true  # skip auth for development
  
database:
  url: "${DATABASE_URL}"
  pool_size: 10
  
search:
  type: "fulltext"  # or "hybrid" for Phase C
  default_limit: 10
  
staleness:
  threshold_days: 90
```

## Deployment

### Container images

- `remember-server:latest` — FastMCP server
- `remember-db:latest` — Postgres + pgvector (optional, can use managed service)

### Kubernetes

Helm chart provided for easy installation:

```bash
helm install remember remember/remember \
  --set auth.providers[0].type=github \
  --set auth.providers[0].client_id=... \
  --set database.url=...
```

### Local development

```bash
# Using Podman
podman build -f Dockerfile.podman -t remember-server .
podman run -p 8000:8000 remember-server

# Using Docker
docker build -f Dockerfile.docker -t remember-server .
docker run -p 8000:8000 remember-server
```

## MCP Tool Surface

All tools enforce identity-based caller authentication. Write tools enforce ownership.

### Read tools

| Tool | Purpose |
|------|---------|
| `team_memory_search(query, types?, tags?, limit=10)` | Full-text search. Returns ranked metadata (no body). |
| `team_memory_get(id)` | Full memory incl. body, history count, confirmations. Logs access. |
| `team_memory_list(owner?, type?, tag?, status='active', updated_since?)` | Paginated browse. |
| `team_memory_stale(threshold_days=90)` | Returns memories older than threshold. |

### Write tools (owner-enforced)

| Tool | Purpose |
|------|---------|
| `team_memory_save(name, type, description, body, tags?, import_source?, preserve_created_at?)` | Upsert on `(owner_id, name)`. Previous version → history. Rejects `type` outside `{'project', 'reference'}` at the tool boundary. |
| `team_memory_verify(id)` | Bump `last_verified_at` without editing body. |
| `team_memory_archive(id)` | Set `status = 'archived'`. |

### Community tools (any user)

| Tool | Purpose |
|------|---------|
| `team_memory_confirm(id, note?)` | Add a confirmation row. Raises confidence signal. |
| `team_memory_refute(id, reason)` | Set `status = 'disputed'`, notify owner via configured channel. |

### Admin tool (Phase 2)

| Tool | Purpose |
|------|---------|
| `team_memory_transfer_owner(id, new_owner_user_id)` | Reassign ownership when a user leaves the team. |

## Phases

### Phase 1 (MVP)
- [ ] Server skeleton (FastMCP + DB schema)
- [ ] GitHub OAuth + API keys + dev mode
- [ ] Podman containerization
- [ ] Basic K8s manifests (Deployment, Service)
- [ ] CLI tool (import/export)
- [ ] Memory policy plugin for AI assistants

### Phase 2
- [ ] Helm chart
- [ ] Ingress/TLS
- [ ] Auto-scaling
- [ ] Monitoring/logging
- [ ] Additional auth providers (Tailscale, Google, Microsoft)

### Phase 3
- [ ] Self-hosted IdP support (Keycloak, Authentik, Dex)
- [ ] pgvector integration for semantic search
- [ ] Hybrid RAG system
- [ ] Slack/Teams notifications
- [ ] Web UI (optional)

### Phase 4
- [ ] Multi-cluster deployment
- [ ] Advanced ACLs
- [ ] Memory-to-memory relationships
- [ ] Automated knowledge extraction from git/Slack/Jira

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
