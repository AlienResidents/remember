---
type: Source Code
description: "/**"
resource: extension/pi/client.ts
timestamp: 2026-07-09T13:54:48Z
---

# client

Source path: `extension/pi/client.ts`

## Content

```typescript
/**
 * MCP client for the REMEMBER server.
 *
 * The server runs in stateless_http mode (no in-memory sessions), so each
 * request is standalone — any pod can serve any request. This lets the
 * server scale horizontally behind a load balancer.
 *
 * Handles:
 *   - OAuth client_credentials flow with token caching
 *     (credentials read from ~/.pi/agent/auth.json under "remember-mcp")
 *   - MCP streamable HTTP tools/call (stateless — no initialize handshake)
 *   - SSE + JSON response parsing
 *   - Automatic token refresh on 401
 */

import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

// ---------------------------------------------------------------------------
// Auth: read credentials from ~/.pi/agent/auth.json, fetch + cache tokens
// ---------------------------------------------------------------------------

interface AuthEntry {
  clientId: string;
  clientSecret: string;
  tokenUrl: string;
}

interface TokenCache {
  token: string;
  expiresAt: number; // epoch ms
}

let tokenCache: TokenCache | null = null;

function readAuthEntry(key: string): AuthEntry {
  const authPath = join(homedir(), ".pi", "agent", "auth.json");
  let raw: string;
  try {
```

*…truncated — full source at `extension/pi/client.ts`*
