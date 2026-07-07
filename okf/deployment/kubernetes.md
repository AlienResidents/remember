---
type: deployment
title: Kubernetes
description: Kubernetes manifests for production deployment. Two containers per pod: server (MCP) + webui (sidecar).
resource: k8s/base/
tags: [kubernetes, deployment, production, sidecar]
timestamp: 2026-07-07T00:00:00Z
---

# Kubernetes

## Overview

Kubernetes manifests for production deployment. Includes Deployment, Service, Ingress, HPA, PDB, and Secret examples.

## Components

| Manifest | Purpose |
|----------|---------|
| `server-deployment.yaml` | Deployment with server + webui sidecar containers |
| `server-service.yaml` | ClusterIP service exposing ports 8000 (MCP) and 3000 (webui) |
| `ingress.yaml` | Ingress routing `/mcp` → server:8000, `/` → webui:3000 |
| `hpa.yaml` | Horizontal pod autoscaler (2-10 replicas) |
| `pdb.yaml` | Pod disruption budget (minAvailable: 1) |
| `secret-example.yaml` | Secret template (fill in values) |

## Container Architecture

Each pod runs two containers:

| Container | Image Command | Port | Purpose |
|-----------|---------------|------|---------|
| `server` | `uvicorn remember.server:app` | 8000 | FastMCP server for AI assistants |
| `webui` | `python -m remember.web` | 3000 | Sci-fi themed web interface |

## Deployment

```bash
# Manual manifests
kubectl apply -f k8s/base/

# Helm chart (preferred)
helm install remember helm/remember -f my-values.yaml
```

## Related Concepts

* [Container Build](container.md)
* [Helm Chart](helm.md)
* [Server](../server.md)
