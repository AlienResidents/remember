---
type: Source Code
description: "/**"
resource: extension/pi/index.ts
timestamp: 2026-07-09T13:54:48Z
---

# index

Source path: `extension/pi/index.ts`

## Content

```typescript
/**
 * REMEMBER Pi Extension
 *
 * Connects to the REMEMBER MCP server and registers its tools in pi.
 *
 * Auth: reads OAuth client_credentials from ~/.pi/agent/auth.json
 * under the "remember-mcp" key. The extension manages token fetching
 * and caching itself — it does NOT rely on pi's built-in MCP server
 * configuration in settings.json.
 *
 * The extension implements the MCP streamable HTTP transport directly:
 *   1. OAuth client_credentials → bearer token (cached, auto-refresh)
 *   2. MCP initialize handshake → capture Mcp-Session-Id
 *   3. tools/call → execute and return content
 *
 * Tools registered:
 *   remember__search_memories
 *   remember__get_memory
 *   remember__list_memories
 *   remember__get_stale_memories
 *   remember__save_memory
 *   remember__verify_memory
 *   remember__archive_memory
 *   remember__confirm_memory
 *   remember__refute_memory
 *
 * State directory:
 *   ~/.pi/agent/state/remember/ — stores connection state and cached
 *   tool lists.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

import { RememberMcpClient } from "./client";

const LABEL = "REMEMBER";
const PREFIX = "remember__";
const DEFAULT_URL = "https://remember.cdd.net.au/mcp";

/**
```

*…truncated — full source at `extension/pi/index.ts`*
