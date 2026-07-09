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
    raw = readFileSync(authPath, "utf8");
  } catch {
    throw new Error(`Cannot read ${authPath} — ensure ~/.pi/agent/auth.json exists`);
  }

  let auth: Record<string, unknown>;
  try {
    auth = JSON.parse(raw);
  } catch {
    throw new Error(`Cannot parse ${authPath} — invalid JSON`);
  }

  const entry = auth[key] as AuthEntry | undefined;
  if (!entry) {
    throw new Error(`No "${key}" entry in ${authPath}`);
  }
  if (!entry.clientId || !entry.clientSecret || !entry.tokenUrl) {
    throw new Error(
      `"${key}" entry in ${authPath} missing required fields (clientId, clientSecret, tokenUrl)`,
    );
  }
  return entry;
}

async function getAccessToken(): Promise<string> {
  // Return cached token if still valid (5s buffer for clock skew)
  if (tokenCache && Date.now() < tokenCache.expiresAt - 5000) {
    return tokenCache.token;
  }

  const creds = readAuthEntry("remember-mcp");
  const response = await fetch(creds.tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "client_credentials",
      client_id: creds.clientId,
      client_secret: creds.clientSecret,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`OAuth token fetch failed (${response.status}): ${text}`);
  }

  const data = (await response.json()) as { access_token: string; expires_in?: number };
  tokenCache = {
    token: data.access_token,
    expiresAt: Date.now() + (data.expires_in ?? 60) * 1000,
  };
  return data.access_token;
}

/** Clear the cached token — used when a 401 is received. */
export function clearTokenCache(): void {
  tokenCache = null;
}

// ---------------------------------------------------------------------------
// MCP streamable HTTP client
// ---------------------------------------------------------------------------

export interface McpToolResult {
  content: Array<{ type: string; text?: string }>;
  isError?: boolean;
}

export class RememberMcpClient {
  private readonly baseUrl: string;
  private requestCounter = 0;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private nextId(): number {
    return ++this.requestCounter;
  }

  /**
   * Call a tool on the MCP server (stateless — no session handshake).
   * Handles token refresh (401) with one retry.
   */
  async callTool(name: string, args: Record<string, unknown>): Promise<McpToolResult> {
    try {
      return await this.callToolInternal(name, args);
    } catch (e) {
      if (isAuthError(e)) {
        // Token expired — refresh and retry
        clearTokenCache();
        return this.callToolInternal(name, args);
      }
      throw e;
    }
  }

  private async callToolInternal(
    name: string,
    args: Record<string, unknown>,
  ): Promise<McpToolResult> {
    const token = await getAccessToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      Authorization: `Bearer ${token}`,
    };

    const response = await fetch(this.baseUrl, {
      method: "POST",
      headers,
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: this.nextId(),
        method: "tools/call",
        params: { name, arguments: args },
      }),
    });

    if (response.status === 401) {
      throw new Error("MCP 401: bearer token rejected");
    }
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`MCP tools/call failed (${response.status}): ${text.slice(0, 500)}`);
    }

    return this.parseResponse(response);
  }

  // --- Response parsing ---

  private async parseResponse(response: Response): Promise<any> {
    const contentType = response.headers.get("content-type") ?? "";

    if (contentType.includes("text/event-stream")) {
      return this.parseSse(await response.text());
    }
    if (contentType.includes("application/json")) {
      const json = await response.json();
      if (json.error) {
        throw new Error(`MCP error: ${json.error.message ?? JSON.stringify(json.error)}`);
      }
      return json.result ?? json;
    }

    // Fallback: try SSE then JSON
    const text = await response.text();
    try {
      return this.parseSse(text);
    } catch {
      try {
        return JSON.parse(text);
      } catch {
        throw new Error(
          `Cannot parse MCP response (content-type: ${contentType}): ${text.slice(0, 200)}`,
        );
      }
    }
  }

  private parseSse(text: string): any {
    const events = text.split(/\n\n+/);
    for (const event of events) {
      const dataLines = event
        .split("\n")
        .filter((l) => l.startsWith("data:"));
      if (dataLines.length === 0) continue;

      // SSE data: lines are concatenated with \n; strip "data:" prefix and leading space
      const data = dataLines
        .map((l) => l.slice(5).replace(/^ /, ""))
        .join("\n");

      try {
        const parsed = JSON.parse(data);
        if (parsed.error) {
          throw new Error(
            `MCP error: ${parsed.error.message ?? JSON.stringify(parsed.error)}`,
          );
        }
        return parsed.result ?? parsed;
      } catch (e) {
        // Re-throw MCP protocol errors
        if (e instanceof Error && e.message.startsWith("MCP error:")) {
          throw e;
        }
        // Skip non-JSON data lines (comments, keepalives)
      }
    }
    throw new Error("No JSON-RPC response in SSE stream");
  }
}

// ---------------------------------------------------------------------------
// Error classification helpers
// ---------------------------------------------------------------------------

function isAuthError(e: unknown): boolean {
  return e instanceof Error && e.message.includes("401");
}