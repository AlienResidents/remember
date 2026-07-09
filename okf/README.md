---
type: Documentation
description: "REMEMBER"
resource: README.md
timestamp: 2026-07-09T01:43:38Z
---

# README

Source path: `README.md`

## Content

# REMEMBER

**Recursive Enhanced Memory by Enhanced Recall**

A shared, team-scoped memory system for developer sessions. Stores collective knowledge and makes it available across team members' AI assistant sessions.

## Overview

REMEMBER provides a shared memory layer that allows teams to:
- Store and retrieve collective knowledge
- Maintain context across sessions and projects
- Share insights and learnings across the team
- Build a persistent organizational memory

![REMEMBER Web UI](docs/images/remember-webui.png)

## Features

- **Team-scoped memory** — share knowledge across your team
- **Ownership-based truth** — creators own their memories, others can confirm/refute
- **Staleness surfacing** — automatically flags outdated memories
- **Multiple auth providers** — GitHub, Google, Microsoft, Tailscale, Keycloak, Authentik, Dex, API keys, and dev mode
- **Kubernetes-native** — deploy anywhere with Helm or kubectl
- **Container-first** — Podman and Docker support
- **Extensible** — pluggable auth, search, and notification layers

## Web UI

A sci-fi themed web interface is included for browsing and managing memories without an AI assistant.

## Knowledge Bundle

System documentation is organized as an [OKF knowledge bundle](okf/index.md) — a structured collection of reference documents covering server architecture, all authentication providers, the full MCP tool surface, database schema, deployment options, and the web UI. Read [okf/index.md](okf/index.md) for a complete walkthrough of how the system works and where to find details on any component.

## Architecture

```
Developer workstations                    Kubernetes Cluster
┌─────────────────────┐              ┌──────────────────────────┐
│ AI Assistant        │              │ namespace: remember      │
│  + memory plugin    │              │                          │
│  + CLI tool         │──MCP/HTTPS──▶│  ┌────────────────────┐  │
└─────────────────────┘              │  │ remember-server    │  │
                                     │  │ (FastMCP, Python)  │  │
                                     │  │ + webui sidecar    │  │
                                     │  │ N replicas, state- │  │
                                     │  │ less               │  │
                                     │  └──────┬───────┬─────┘  │
                                     │         │       │        │
                                     │    MCP  │  SQL  │ /      │
                                     │  (tools) │       │ (web)  │
                                     │          ▼       ▼        │
                                     │  ┌────────────────────────┐│
                                     │  │ remember-db            ││
                                     │  │ Postgres + pgvector    ││
                                     │  └────────────────────────┘│
                                     └──────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **AI Assistant** | MCP client (Claude Code, etc.) connecting via Model Context Protocol |
| **CLI** | Local import/export and management tool |
| **Web UI** | Sci-fi themed FastAPI interface on port 3000 (sidecar or separate) |
| **remember-server** | Stateless FastMCP server, horizontally scalable |
| **remember-db** | Postgres with pgvector for semantic search |

### Authentication

Pluggable auth providers (configured via env vars or YAML):
- GitHub OAuth, Google OAuth, Microsoft/Entra ID
- Tailscale identity, Keycloak, Authentik, Dex
- API keys, dev mode

### Ports

| Port | Service |
|------|---------|
| 8000 | MCP server (FastMCP) |
| 3000 | Web UI (FastAPI) |
| 9090 | Prometheus metrics |

## Getting Started

See the [design docs](docs/design.md) for architecture details and the [deployment guide](docs/deployment.md) for setup instructions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
