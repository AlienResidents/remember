---
type: server
title: REMEMBER Server
description: Stateless FastMCP server for team memory storage and retrieval. Horizontally scalable with pluggable authentication.
resource: https://github.com/AlienResidents/remember
tags: [fastmcp, python, stateless, mcp]
timestamp: 2026-07-06T00:00:00Z
---

# REMEMBER Server

## Overview

Stateless FastMCP server that provides team memory storage and retrieval via the Model Context Protocol. All state lives in Postgres, enabling horizontal scaling and zero-downtime deployments.

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

## Key Design Decisions

### Stateless server

The server maintains no local state. All state lives in Postgres. This enables:
- Horizontal scaling (add replicas as needed)
- Zero-downtime deployments (RollingUpdate)
- Simple disaster recovery (restore from DB backup)

### Identity providers

Support multiple identity providers via a pluggable auth layer (see [Auth Middleware](auth/middleware.md)).

### Database migrations

Schema changes use Alembic for Python. Migrations are version-controlled and applied automatically on server startup.

## Configuration

All configuration via environment variables (prefixed `REMEMBER_`) or YAML config.

| Variable | Description | Default |
|----------|-------------|---------|
| `REMEMBER_DATABASE_URL` | Postgres connection string | `postgresql+asyncpg://localhost:5432/remember` |
| `REMEMBER_SERVER_HOST` | Bind address | `0.0.0.0` |
| `REMEMBER_SERVER_PORT` | Bind port | `8000` |
| `REMEMBER_AUTH_DEV_MODE` | Enable dev auth | `false` |
| `REMEMBER_SEARCH_TYPE` | Search type | `fulltext` |
| `REMEMBER_STALENESS_THRESHOLD_DAYS` | Staleness threshold | `90` |

See [config.example.yaml](../../server/config.example.yaml) for full YAML format.

## Monitoring

| Endpoint | Purpose |
|----------|---------|
| `/healthz` | Health check |
| `/metrics` | Prometheus metrics |

## Related Concepts

* [Auth Middleware](auth/middleware.md)
* [MCP Tools](tools/overview.md)
* [Database Schema](models/schema.md)
* [Deployment](deployment/kubernetes.md)
