---
type: Source Code
description: "/**"
resource: extension/pi/index.ts
timestamp: 2026-07-09T01:43:38Z
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
 * The REMEMBER server exposes an MCP endpoint (typically at
 * https://remember.cdd.net.au/mcp or via stdio when running locally).
 * This extension uses the existing `mcp` extension's connection
 * management to talk to that endpoint, then registers the tools
 * under the `remember` namespace.
 *
 * Configuration:
 *   - The REMEMBER MCP server must be configured in `.pi/settings.json`
 *     under the `mcp.servers.remember` key (or globally in
 *     `~/.pi/agent/settings.json`).
 *   - Example:
 *       {
 *         "mcp": {
 *           "servers": {
 *             "remember": {
 *               "transport": "http",
 *               "url": "https://remember.cdd.net.au/mcp",
 *               "auth": "none"
 *             }
 *           }
 *         }
 *       }
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
```

*…truncated — full source at `extension/pi/index.ts`*
