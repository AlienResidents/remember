# REMEMBER Server

FastMCP server for team memory storage and retrieval.

## Features

- **Stateless** — horizontal scaling, zero-downtime deployments
- **Pluggable auth** — GitHub OAuth, API keys, Tailscale, Keycloak, and more
- **Full-text search** — built-in search with pgvector for future semantic search
- **Ownership model** — creators own memories, others can confirm/refute
- **Staleness detection** — automatically flags outdated memories
- **MCP protocol** — integrates with AI assistants via Model Context Protocol

## Architecture

The server is a stateless FastMCP application that:
1. Authenticates callers via configured identity providers
2. Maps identity to a `users` row in Postgres
3. Enforces ownership on write operations
4. Provides read/write tools via MCP

## Setup

See [docs/design.md](../docs/design.md) for full architecture details.

### Prerequisites

- Python 3.11+
- Postgres 16+ with pgvector extension
- (Optional) Redis for session caching

### Installation

```bash
# Clone the repo
git clone https://github.com/AlienResidents/remember.git
cd remember/server

# Install dependencies
pip install -e .

# Run migrations
alembic upgrade head

# Start the server
python -m remember.server --config config.yaml
```

### Configuration

See [config.example.yaml](config.example.yaml) for all options.

Key configuration:
- `server.host` / `server.port` — bind address
- `auth.providers` — identity providers to enable
- `database.url` — Postgres connection string
- `search.type` — `fulltext` or `hybrid` (Phase C)

## Development

```bash
# Run with dev config (skips auth)
python -m remember.server --config config.dev.yaml

# Run migrations
alembic upgrade head

# Run tests
pytest
```

## API

The server exposes tools via MCP. See [docs/design.md](../docs/design.md#mcp-tool-surface) for the full tool list.

## License

MIT
