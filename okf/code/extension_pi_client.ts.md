---
type: Source Code
description: "/**"
resource: extension/pi/client.ts
timestamp: 2026-07-09T13:05:52Z
---

# client

Source path: `extension/pi/client.ts`

## Content

```typescript
/**
 * MCP client for the REMEMBER server.
 *
 * Handles:
 *   - OAuth client_credentials flow with token caching
 *     (credentials read from ~/.pi/agent/auth.json under "remember-mcp")
 *   - MCP streamable HTTP session management
 *     (initialize → capture Mcp-Session-Id → tools/call)
 *   - SSE response parsing
 *   - Automatic token refresh and session re-init on failure
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
    raw = readFileSync(authPath, "utf8");
  } catch {
    throw new Error(`Cannot read ${authPath} — ensure ~/.pi/agent/auth.json exists`);
```

*…truncated — full source at `extension/pi/client.ts`*
