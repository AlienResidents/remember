---
type: deployment
title: Container Build
description: Podman and Docker containerization for the REMEMBER server.
resource: server/Containerfile
tags: [container, podman, docker, containerfile]
timestamp: 2026-07-06T00:00:00Z
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
podman run -p 8000:8000 \
  -e REMEMBER_DATABASE_URL=postgresql+asyncpg://db:5432/remember \
  -e REMEMBER_AUTH_DEV_MODE=true \
  remember-server:latest
```

## Image Details

| Property | Value |
|----------|-------|
| Base image | python:3.14-slim |
| User | non-root (`remember`) |
| Filesystem | read-only (except `/tmp`) |
| Exposed port | 8000 |
| Entrypoint | `python -m remember.server` |

## Related Concepts

* [Kubernetes](kubernetes.md)
* [Helm Chart](helm.md)
* [Server](../server.md)
