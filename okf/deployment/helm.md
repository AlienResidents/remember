---
type: deployment
title: Helm Chart
description: Helm chart for easy REMEMBER deployment and configuration. Includes webui sidecar and oauth2-proxy integration.
resource: helm/remember/
tags: [helm, charts, deployment, sidecar, oauth2]
timestamp: 2026-07-07T00:00:00Z
---

# Helm Chart

## Overview

Helm chart for REMEMBER with configurable values for auth, database, autoscaling, and ingress.

## Structure

```
helm/remember/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── _helpers.tpl
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    └── pdb.yaml
```

## Key Values

| Value | Description | Default |
|-------|-------------|---------|
| `server.replicaCount` | Number of replicas | `2` |
| `server.autoscaling.enabled` | Enable HPA | `true` |
| `server.autoscaling.minReplicas` | Min replicas | `2` |
| `server.autoscaling.maxReplicas` | Max replicas | `10` |
| `auth.devMode` | Enable dev auth | `false` |
| `auth.github.enabled` | Enable GitHub OAuth | `false` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class (traefik/nginx) | `nginx` |
| `ingress.middlewares` | Traefik middlewares (oauth2-proxy, etc.) | `traefik-https-redirect@kubernetescrd` |
| `database.url` | Database connection string | Required |
| `webui.enabled` | Enable webui sidecar | `true` |
| `webui.replicaCount` | Webui replicas | `1` |

## Install

```bash
helm install remember helm/remember -f my-values.yaml
```

## Related Concepts

* [Container Build](container.md)
* [Kubernetes](kubernetes.md)
* [Server](../server.md)
