---
type: webui
title: Web Interface
description: Sci-fi themed FastAPI web UI for browsing and managing memories.
resource: webui/
tags: [webui, fastapi, sci-fi]
timestamp: 2026-07-06T00:00:00Z
---

# Web Interface

## Overview

Sci-fi themed web interface for browsing and managing memories without an AI assistant. Built with FastAPI, vanilla JS, and CSS animations.

## Features

- Animated grid background with floating particles
- Rotating holographic logo with neon glow
- Search with type/status filters
- Memory detail view with markdown rendering
- Create/edit memories form
- Verify/Archive/Refute actions
- Toast notifications
- Responsive design

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| Frontend | Vanilla JS, CSS animations |
| Styling | Custom sci-fi theme (neon cyan/purple) |
| Fonts | Orbitron (display), Rajdhani (body) |

## Running

```bash
cd server
python -m remember.web
# Serves on http://localhost:3000
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Web UI |
| `/healthz` | GET | Health check |
| `/api/search` | GET | Search memories |
| `/api/get/{id}` | GET | Get memory details |
| `/api/save` | POST | Create/update memory |
| `/api/verify/{id}` | POST | Verify memory |
| `/api/archive/{id}` | POST | Archive memory |
| `/api/refute/{id}` | POST | Refute memory |

## Related Concepts

* [Server](server.md)
* [Tools Overview](tools/overview.md)
