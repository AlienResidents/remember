# REMEMBER Deployment Guide

## Local Development

### Using Podman

```bash
cd server

# Build the image
podman build -f Containerfile -t remember-server:latest .

# Run the container
podman run -p 8000:8000 \
  -e REMEMBER_DATABASE_URL=postgresql+asyncpg://localhost:5432/remember \
  -e REMEMBER_AUTH_DEV_MODE=true \
  remember-server:latest
```

### Using Docker

```bash
cd server

# Build the image
docker build -f Dockerfile -t remember-server:latest .

# Run the container
docker run -p 8000:8000 \
  -e REMEMBER_DATABASE_URL=postgresql+asyncpg://localhost:5432/remember \
  -e REMEMBER_AUTH_DEV_MODE=true \
  remember-server:latest
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.25+)
- Helm 3.x
- Ingress controller (nginx recommended)
- cert-manager (for TLS)
- Postgres database (managed or self-hosted)

### Install with Helm

```bash
# Add the chart repository
helm repo add remember https://alienresidents.github.io/remember
helm repo update

# Create a values custom file
cat > my-values.yaml << EOF
server:
  image:
    repository: remember-server
    tag: latest

database:
  url: postgresql+asyncpg://user:password@db-host:5432/remember

auth:
  devMode: false
  github:
    enabled: true
    clientId: your-client-id
    clientSecret: your-client-secret

ingress:
  enabled: true
  hosts:
    - host: remember.example.com
      paths:
        - path: /mcp
          pathType: Prefix
EOF

# Install the chart
helm install remember remember/remember -f my-values.yaml
```

### Manual K8s Manifests

```bash
# Apply base manifests
kubectl apply -f k8s/base/

# Apply secrets (edit secret-example.yaml first)
kubectl apply -f k8s/base/secret.yaml

# Verify deployment
kubectl get pods -l app=remember
kubectl get services -l app=remember
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REMEMBER_DATABASE_URL` | Postgres connection string | `postgresql+asyncpg://localhost:5432/remember` |
| `REMEMBER_SERVER_HOST` | Bind address | `0.0.0.0` |
| `REMEMBER_SERVER_PORT` | Bind port | `8000` |
| `REMEMBER_SERVER_WORKERS` | Number of workers | `2` |
| `REMEMBER_AUTH_DEV_MODE` | Enable dev auth (skip auth) | `false` |
| `REMEMBER_SEARCH_TYPE` | Search type (fulltext/hybrid) | `fulltext` |
| `REMEMBER_SEARCH_DEFAULT_LIMIT` | Default search limit | `10` |
| `REMEMBER_STALENESS_THRESHOLD_DAYS` | Days before marking as stale | `90` |

### Database Setup

The server expects a Postgres 16+ database with pgvector extension:

```sql
CREATE DATABASE remember;
CREATE EXTENSION IF NOT EXISTS pgvector;
```

Run migrations on first deploy:

```bash
cd server
alembic upgrade head
```

## Monitoring

The server exposes:
- `/healthz` — Health check endpoint
- `/metrics` — Prometheus metrics (request rate, response latency, tool calls, DB connections)

### Helm Values

See [helm/remember/values.yaml](../helm/remember/values.yaml) for all configurable options.

## Upgrading

### Upgrade Helm Release

```bash
helm upgrade remember remember/remember -f my-values.yaml
```

### Database Migrations

Migrations run automatically on server startup. For manual migration:

```bash
cd server
alembic upgrade head
```

## Troubleshooting

### Pod won't start

Check events:
```bash
kubectl describe pod -l app=remember
```

Check logs:
```bash
kubectl logs -l app=remember
```

### Database connection failures

Verify database URL is correct and database is accessible:
```bash
kubectl exec -it <pod> -- python -c "import sqlalchemy; sqlalchemy.create_engine('<url>').connect()"
```

### Auth failures

Check auth provider configuration in secrets/configmap.

## Web UI

The web UI is a separate FastAPI application that serves the sci-fi themed interface on port 3000. It provides REST API endpoints for browsing and managing memories without an AI assistant.

### Local Development

```bash
cd server
python -m remember.web
# Serves on http://localhost:3000
```

### Kubernetes Deployment

The web UI can be deployed as a separate service or alongside the main server.

#### Option 1: Separate Deployment

```bash
# Apply web UI manifests
kubectl apply -f k8s/webui/
```

#### Option 2: Combined with Main Server

Update the Helm chart to include the web UI in the main deployment (see Helm values).

### Web UI Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `WEBUI_HOST` | Bind address | `0.0.0.0` |
| `WEBUI_PORT` | Bind port | `3000` |

The web UI shares the same database as the main server and uses the same auth configuration.

### Ingress

Add the web UI to your ingress configuration:

```yaml
ingress:
  hosts:
    - host: remember.example.com
      paths:
        - path: /mcp
          pathType: Prefix
        - path: /
          pathType: Prefix
```

The web UI serves on `/` while the MCP endpoint is on `/mcp`.
