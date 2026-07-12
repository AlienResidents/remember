---
type: Configuration
description: "# REMEMBER Server Environment Variables"
resource: server/.env.example
timestamp: 2026-07-12T01:50:00Z
---

# .env

Source path: `server/.env.example`

## Content

```bash
# REMEMBER Server Environment Variables
# Copy this file to .env and adjust as needed

# Database (note: double-underscore for nested settings)
REMEMBER_DATABASE__URL=postgresql+asyncpg://localhost:5432/remember

# Server
REMEMBER_SERVER__HOST=0.0.0.0
REMEMBER_SERVER__PORT=8000
REMEMBER_SERVER__WORKERS=2
REMEMBER_SERVER__LOG_LEVEL=INFO

# Auth — shared
REMEMBER_AUTH__DEV_MODE=true

# Auth — MCP server (bearer token / client_credentials flow)
REMEMBER_AUTH__KEYCLOAK_AUTHORITY=https://keycloak.example.com
REMEMBER_AUTH__KEYCLOAK_REALM=master
# For MCP server: the machine client ID (azp claim check)
# For Web UI: the browser client ID (authorization_code flow)
REMEMBER_AUTH__KEYCLOAK_CLIENT_ID=remember-pi

# Auth — MCP server JWKS override (optional)
# Set to an in-cluster service URL to bypass ingress for JWKS fetches.
# If empty, derived from KEYCLOAK_AUTHORITY. The issuer claim is always
# derived from KEYCLOAK_AUTHORITY (must match the external URL in JWTs).
# Example: http://keycloak.keycloak.svc.cluster.local:8080/realms/master/protocol/openid-connect/certs
REMEMBER_AUTH__KEYCLOAK_JWKS_URL=
# For Web UI only: client secret for authorization_code exchange
REMEMBER_AUTH__KEYCLOAK_CLIENT_SECRET=

# Auth — Web UI session
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
REMEMBER_AUTH__SESSION_SECRET=

# Search
REMEMBER_SEARCH__TYPE=fulltext
REMEMBER_SEARCH__DEFAULT_LIMIT=10

# Staleness
REMEMBER_STALENESS__THRESHOLD_DAYS=90
```
