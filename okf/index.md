# REMEMBER — Knowledge Bundle

**OKF v0.1 Knowledge Bundle** for the REMEMBER team memory system. Covers the server architecture, authentication providers, MCP tools, data model, deployment, and web UI.

## Sections

### Server
* [Server Overview](server.md) - FastMCP server architecture, stateless design, horizontal scaling

### Authentication
* [Auth Middleware](auth/middleware.md) - Pluggable authentication layer with provider registration
* [GitHub OAuth](auth/github.md) - GitHub OAuth2 authentication provider
* [Google OAuth](auth/google.md) - Google OAuth2 authentication provider
* [Microsoft OAuth](auth/microsoft.md) - Microsoft/Entra ID OAuth2 authentication provider
* [Tailscale Identity](auth/tailscale.md) - Tailscale tailnet user authentication
* [Keycloak](auth/keycloak.md) - Self-hosted Keycloak OAuth2/OIDC provider
* [Authentik](auth/authentik.md) - Self-hosted Authentik OAuth2 provider
* [Dex](auth/dex.md) - Dex OIDC provider for Kubernetes environments
* [API Key](auth/api_key.md) - Static API key authentication
* [Dev Mode](auth/dev.md) - Development mode (skip authentication)

### Tools
* [MCP Tools Overview](tools/overview.md) - Full tool surface with signatures and behavior
* [Search](tools/search.md) - Full-text search with PostgreSQL `to_tsvector`
* [Search Vector](tools/search_vector.md) - pgvector semantic search with cosine similarity
* [Save](tools/save.md) - Upsert memory with history tracking
* [Get](tools/get.md) - Retrieve memory with access logging
* [List](tools/list.md) - Paginated memory listing with filters
* [Stale](tools/stale.md) - Identify memories past verification threshold
* [Verify](tools/verify.md) - Bump last_verified_at (owner only)
* [Archive](tools/archive.md) - Set status to archived (owner only)
* [Confirm](tools/confirm.md) - Add confirmation, remove existing refutation
* [Refute](tools/refute.md) - Add refutation, mark disputed on first

### Data Model
* [Database Schema](models/schema.md) - Complete SQL schema with constraints and indexes

### Deployment
* [Container Build](deployment/container.md) - Podman/Docker containerization
* [Kubernetes](deployment/kubernetes.md) - K8s manifests and Helm chart
* [Helm Chart](deployment/helm.md) - Helm chart values and templates

### Web UI
* [Web Interface](webui.md) - Sci-fi themed FastAPI web UI
