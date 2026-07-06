---
type: deployment
title: Kubernetes
description: Kubernetes manifests for production deployment.
resource: k8s/base/
tags: [kubernetes, deployment, production]
timestamp: 2026-07-06T00:00:00Z
---

# Kubernetes

## Overview

Kubernetes manifests for production deployment. Includes Deployment, Service, Ingress, HPA, PDB, and Secret examples.

## Components

| Manifest | Purpose |
|----------|---------|
| `server-deployment.yaml` | Stateless server deployment (2 replicas default) |
| `server-service.yaml` | ClusterIP service on port 8000 |
| `ingress.yaml` | Ingress with `/mcp` path |
| `hpa.yaml` | Horizontal pod autoscaler (2-10 replicas) |
| `pdb.yaml` | Pod disruption budget (minAvailable: 1) |
| `secret-example.yaml` | Secret template (fill in values) |

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
