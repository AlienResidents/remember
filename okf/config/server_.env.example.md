---
type: Configuration
description: "# REMEMBER Server Environment Variables"
resource: server/.env.example
timestamp: 2026-07-09T01:43:39Z
---

# .env

Source path: `server/.env.example`

## Content

```bash
# REMEMBER Server Environment Variables
# Copy this file to .env and adjust as needed

# Database
REMEMBER_DATABASE_URL=postgresql+asyncpg://localhost:5432/remember

# Server
REMEMBER_SERVER_HOST=0.0.0.0
REMEMBER_SERVER_PORT=8000
REMEMBER_SERVER_WORKERS=2

# Auth
REMEMBER_AUTH_DEV_MODE=true

# Search
REMEMBER_SEARCH_TYPE=fulltext
REMEMBER_SEARCH_DEFAULT_LIMIT=10

# Staleness
REMEMBER_STALENESS_THRESHOLD_DAYS=90

```
