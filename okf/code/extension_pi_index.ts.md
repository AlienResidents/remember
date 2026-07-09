---
type: Source Code
description: "/**"
resource: extension/pi/index.ts
timestamp: 2026-07-09T14:09:52Z
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
 * The server runs in stateless_http mode — each tools/call is standalone,
 * no initialize handshake or session tracking needed.
 *
 * Identity resolution (two-tier):
 *   Option B (primary): read username from ~/.pi/agent/settings.json
 *     under "remember.username" and inject it as the identity param
 *     (owner_id / owner / user_id) into every tool call that needs it.
 *     The LLM never sees these params — they're injected silently.
 *     The server resolves username → UUID via get-or-create on User
 *     (provider="keycloak", provider_id=<username>).
 *   Option A (fallback): if no username configured, calls proceed
 *     without identity and the server derives it from the JWT azp
 *     claim via its client_user_mapping config.
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
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

import { readFileSync } from "node:fs";
import { homedir } from "node:os";
```

*…truncated — full source at `extension/pi/index.ts`*
