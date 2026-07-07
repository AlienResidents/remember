---
type: deployment
title: Container Build
description: Podman and Docker containerization for the REMEMBER server. Single image runs both MCP server and webui sidecar.
resource: server/Containerfile
tags: [container, podman, docker, containerfile, sidecar]
timestamp: 2026-07-07T00:00:00Z
---

# Container Build

## Overview

Two containerfiles: `Containerfile` for Podman (primary) and `Dockerfile` for Docker (compatible). Both produce identical images.

## Building

```bash
# Podman (primary)
cd server
podman build -f Containerfile -t remember-server:latest .

# Docker
cd server
docker build -f Dockerfile -t remember-server:latest .
```

## Running

```bash
# MCP server only
podman run -p 8000:8000 \
  -e REMEMBER_DATABASE_URL=postgresql+asyncpg://db:5432/remember \
  -e REMEMBER_AUTH_DEV_MODE=true \
  remember-server:latest

# Web UI only (sidecar mode)
podman run -p 3000:3000 \
  -e REMEMBER_DATABASE_URL=postgresql+asyncpg://db:5432/remember \
  -e REMEMBER_AUTH_DEV_MODE=true \
  remember-server:latest --command="python -m remember.web"
```

## Image Details

| Property | Value |
|----------|-------|
| Base image | python:3.14-slim |
| User | non-root (`remember`) |
| Filesystem | read-only (except `/tmp`) |
| Exposed ports | 8000 (MCP), 3000 (webui) |
| Entrypoint | `python -m uvicorn remember.server:app` (server) or `python -m remember.web` (webui) |
| Static assets | `webui/` directory (index.html, styles.css, app.js, fonts/) |

## Related Concepts

* [Kubernetes](kubernetes.md)
* [Helm Chart](helm.md)
* [Server](../server.md)
