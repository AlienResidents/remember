---
type: Infrastructure
description: "  host: "0.0.0.0""
resource: server/config.example.yaml
timestamp: 2026-07-09T01:43:39Z
---

# config.example

Source path: `server/config.example.yaml`

## Content

```yaml
# REMEMBER Server Configuration
# Copy this file to config.yaml and adjust as needed

server:
  host: "0.0.0.0"
  port: 8000
  workers: 2

auth:
  providers:
    - type: github
      client_id: "${GITHUB_CLIENT_ID}"
      client_secret: "${GITHUB_CLIENT_SECRET}"
    - type: api_key
      enabled: true
    - type: dev
      enabled: true  # Skip auth for development

database:
  url: "postgresql+asyncpg://localhost:5432/remember"
  echo: false
  pool_size: 10
  max_overflow: 20

search:
  type: "fulltext"  # or "hybrid" for Phase C
  default_limit: 10

staleness:
  threshold_days: 90

```
