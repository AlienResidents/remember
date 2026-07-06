# REMEMBER

**Recursive Enhanced Memory by Enhanced Recall**

A shared, team-scoped memory system for developer sessions. Stores collective knowledge and makes it available across team members' AI assistant sessions.

## Overview

REMEMBER provides a shared memory layer that allows teams to:
- Store and retrieve collective knowledge
- Maintain context across sessions and projects
- Share insights and learnings across the team
- Build a persistent organizational memory

## Features

- **Team-scoped memory** — share knowledge across your team
- **Ownership-based truth** — creators own their memories, others can confirm/refute
- **Staleness surfacing** — automatically flags outdated memories
- **Multiple auth providers** — GitHub OAuth, API keys, Tailscale, Keycloak, and more
- **Kubernetes-native** — deploy anywhere with Helm or kubectl
- **Container-first** — Podman and Docker support
- **Extensible** — pluggable auth, search, and notification layers

## Architecture

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
                                     │  └────────────────────┘  │
                                     └──────────────────────────┘
```

## Getting Started

See the [design docs](docs/design.md) for architecture details and the [deployment guide](docs/deployment.md) for setup instructions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
