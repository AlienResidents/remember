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
| `REMEMBER_DATABASE_URL` | Postgres connection string | Required |
| `REMEMBER_AUTH_DEV_MODE` | Enable dev auth (skip auth) | `false` |
| `REMEMBER_AUTH_GITHUB_CLIENT_ID` | GitHub OAuth client ID | - |
| `REMEMBER_AUTH_GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | - |
| `REMEMBER_SEARCH_TYPE` | Search type (fulltext/hybrid) | `fulltext` |
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

The server exposes a `/healthz` endpoint for health checks.

### Metrics (Phase 2)

Future versions will expose Prometheus metrics:
- Request rate
- Response latency
- Error rate
- Database connection pool stats

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
