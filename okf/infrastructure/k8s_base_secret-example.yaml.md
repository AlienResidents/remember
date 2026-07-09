---
type: Infrastructure
description: "apiVersion: v1"
resource: k8s/base/secret-example.yaml
timestamp: 2026-07-09T13:54:49Z
---

# secret-example

Source path: `k8s/base/secret-example.yaml`

## Content

```yaml
# Example secrets - copy to secret.yaml and fill in values
apiVersion: v1
kind: Secret
metadata:
  name: remember-secrets
  labels:
    app: remember
type: Opaque
stringData:
  # Database connection string
  database-url: "postgresql+asyncpg://user:password@remember-db:5432/remember"
  
  # GitHub OAuth (if using GitHub auth)
  github-client-id: ""
  github-client-secret: ""
  
  # Server configuration
  server-host: "0.0.0.0"
  server-port: "8000"

```
