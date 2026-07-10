---
type: Source Code
description: "/**"
resource: extension/pi/index.ts
timestamp: 2026-07-10T02:44:32Z
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
 * Identity resolution:
 *   The server derives user identity exclusively from the JWT azp claim
 *   (via its client_user_mapping config). The extension does NOT inject
 *   identity params — the server does not trust client-supplied identity.
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

import { RememberMcpClient } from "./client";

const LABEL = "REMEMBER";
const PREFIX = "remember__";
const DEFAULT_URL = "https://remember.cdd.net.au/mcp";

/**
 * Extension factory. Called once when pi loads this extension.
```

*…truncated — full source at `extension/pi/index.ts`*
