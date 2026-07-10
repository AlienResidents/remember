/**
 * MCP client for the REMEMBER server.
 *
 * The server runs in stateless_http mode (no in-memory sessions), so each
 * request is standalone — any pod can serve any request. This lets the
 * server scale horizontally behind a load balancer.
 *
 * Auth: OAuth 2.0 authorization_code + PKCE (RFC 8252 / RFC 7636).
 *   - Public client (no secret — desktop apps can't keep secrets)
 *   - PKCE S256 is the security mechanism
 *   - Local callback server on http://127.0.0.1:8484/callback
 *   - Browser launch with headless fallback (print URL, user pastes redirect)
 *   - Tokens (access + refresh) cached in ~/.pi/agent/auth.json
 *   - Automatic refresh on expiry; re-authorize if refresh fails
 *
 * Identity: the JWT `sub` claim IS the user's Keycloak UUID. The server
 * reads it directly — no client_user_mapping needed.
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { createServer, type Server } from "node:http";
import { spawn } from "node:child_process";
import { randomBytes, createHash } from "node:crypto";
import { networkInterfaces } from "node:os";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const AUTH_KEY = "remember-mcp";
const CALLBACK_PORT = 8484;
const CALLBACK_HOST = "127.0.0.1";
const CALLBACK_PATH = "/callback";
const REDIRECT_URI = `http://${CALLBACK_HOST}:${CALLBACK_PORT}${CALLBACK_PATH}`;
const SCOPES = "openid profile email";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface OAuthConfig {
  clientId: string;
  tokenUrl: string;
  authUrl: string;
  redirectPort?: number;
}

interface StoredTokens {
  accessToken: string;
  refreshToken?: string;
  expiresAt: number; // epoch ms
}

interface TokenCache {
  token: string;
  expiresAt: number; // epoch ms
}

// ---------------------------------------------------------------------------
// PKCE helpers (RFC 7636)
// ---------------------------------------------------------------------------

function base64UrlEncode(buffer: Buffer | string): string {
  const buf = typeof buffer === "string" ? Buffer.from(buffer) : buffer;
  return buf.toString("base64url");
}

function generateCodeVerifier(): string {
  // RFC 7636: 43-128 chars from [A-Z/a-z/0-9-._~]
  return base64UrlEncode(randomBytes(32));
}

function generateCodeChallenge(verifier: string): string {
  // S256: base64url(SHA256(verifier))
  const hash = createHash("sha256").update(verifier).digest();
  return base64UrlEncode(hash);
}

function generateState(): string {
  return base64UrlEncode(randomBytes(16));
}

// ---------------------------------------------------------------------------
// Auth config + token storage (read/write ~/.pi/agent/auth.json)
// ---------------------------------------------------------------------------

function getAuthPath(): string {
  return join(homedir(), ".pi", "agent", "auth.json");
}

function readAuthFile(): Record<string, unknown> {
  const authPath = getAuthPath();
  if (!existsSync(authPath)) {
    throw new Error(`Auth file not found: ${authPath}`);
  }
  try {
    return JSON.parse(readFileSync(authPath, "utf8"));
  } catch (e) {
    throw new Error(`Cannot parse ${authPath}: ${e}`);
  }
}

function writeAuthFile(data: Record<string, unknown>): void {
  writeFileSync(getAuthPath(), JSON.stringify(data, null, 2) + "\n");
}

function readOAuthConfig(): OAuthConfig {
  const auth = readAuthFile();
  const entry = auth[AUTH_KEY] as Partial<OAuthConfig> | undefined;
  if (!entry) {
    throw new Error(
      `No "${AUTH_KEY}" entry in ~/.pi/agent/auth.json. ` +
        `Expected: { clientId, tokenUrl, authUrl }`,
    );
  }
  if (!entry.clientId || !entry.tokenUrl || !entry.authUrl) {
    throw new Error(
      `"${AUTH_KEY}" entry missing required fields (clientId, tokenUrl, authUrl)`,
    );
  }
  return {
    clientId: entry.clientId,
    tokenUrl: entry.tokenUrl,
    authUrl: entry.authUrl,
    redirectPort: entry.redirectPort ?? CALLBACK_PORT,
  };
}

function readStoredTokens(): StoredTokens | null {
  const auth = readAuthFile();
  const entry = auth[AUTH_KEY] as Partial<StoredTokens> | undefined;
  if (!entry?.accessToken) return null;
  return {
    accessToken: entry.accessToken,
    refreshToken: entry.refreshToken,
    expiresAt: entry.expiresAt ?? 0,
  };
}

function writeStoredTokens(tokens: StoredTokens): void {
  const auth = readAuthFile();
  auth[AUTH_KEY] = {
    ...(auth[AUTH_KEY] as Record<string, unknown>),
    accessToken: tokens.accessToken,
    refreshToken: tokens.refreshToken,
    expiresAt: tokens.expiresAt,
  };
  writeAuthFile(auth);
}

function clearStoredTokens(): void {
  const auth = readAuthFile();
  const entry = auth[AUTH_KEY] as Record<string, unknown> | undefined;
  if (entry) {
    delete entry.accessToken;
    delete entry.refreshToken;
    delete entry.expiresAt;
    writeAuthFile(auth);
  }
}

// ---------------------------------------------------------------------------
// Token cache (in-memory, backed by auth.json)
// ---------------------------------------------------------------------------

let tokenCache: TokenCache | null = null;

function isHeadless(): boolean {
  // No DISPLAY on Linux, no TERM_PROGRAM on macOS → likely headless/SSH
  return !process.env.DISPLAY && !process.env.TERM_PROGRAM && !process.env.BROWSER;
}

function openBrowser(url: string): boolean {
  const platform = process.platform;
  let cmd: string;
  let args: string[];

  if (platform === "darwin") {
    cmd = "open";
    args = [url];
  } else if (platform === "win32") {
    cmd = "cmd";
    args = ["/c", "start", "", url];
  } else {
    // Linux/Unix
    cmd = "xdg-open";
    args = [url];
  }

  try {
    spawn(cmd, args, { detached: true, stdio: "ignore" }).unref();
    return true;
  } catch {
    return false;
  }
}

/**
 * Run the full authorization_code + PKCE flow:
 *   1. Generate code_verifier + code_challenge
 *   2. Start local callback server + stdin paste fallback
 *   3. Open browser to Keycloak auth endpoint (prints URL for headless)
 *   4. Wait for callback with authorization code (server or stdin)
 *   5. Exchange code for tokens
 *   6. Store tokens in auth.json
 */
async function authorizeWithPKCE(config: OAuthConfig): Promise<string> {
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);
  const state = generateState();

  // Build auth URL
  const authParams = new URLSearchParams({
    response_type: "code",
    client_id: config.clientId,
    redirect_uri: REDIRECT_URI,
    scope: SCOPES,
    state,
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
  });
  const authUrl = `${config.authUrl}?${authParams.toString()}`;

  // Print the auth URL — always, so headless users can copy it
  console.log("\n=== OAuth Authorization Required ===");
  console.log("Open this URL in your browser to log in:\n");
  console.log(authUrl);
  console.log("");

  // Try to open browser (no-op on headless)
  openBrowser(authUrl);

  // Wait for callback (server or stdin paste) — both run in parallel
  const { code, state: returnedState } = await waitForCallback(state);

  // Verify state (CSRF protection)
  if (returnedState !== state) {
    throw new Error("OAuth state mismatch — possible CSRF attack. Aborting.");
  }

  // Exchange code for tokens
  const tokens = await exchangeCodeForTokens(config, code, codeVerifier);
  writeStoredTokens(tokens);
  tokenCache = { token: tokens.accessToken, expiresAt: tokens.expiresAt };
  return tokens.accessToken;
}

/**
 * Start a local HTTP server on 127.0.0.1:8484 and wait for the OAuth callback.
 * Returns the authorization code and state from the callback.
 */
function waitForCallback(_expectedState: string): Promise<{ code: string; state: string }> {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error("OAuth callback timed out after 5 minutes"));
    }, 5 * 60 * 1000);

    let settled = false;
    let server: Server | null = null;
    let stdinListener: ((chunk: Buffer) => void) | null = null;

    function cleanup(): void {
      clearTimeout(timeout);
      if (server) server.close();
      if (stdinListener) process.stdin.removeListener("data", stdinListener);
      // Don't pause stdin — it might be the process's real stdin (pi's TTY)
    }

    function handleResult(result: { code: string; state: string }): void {
      if (settled) return;
      settled = true;
      cleanup();
      resolve(result);
    }

    function handleError(err: Error): void {
      if (settled) return;
      settled = true;
      cleanup();
      reject(err);
    }

    // --- Mode 1: callback server (local browser or SSH port-forward) ---
    server = createServer((req, res) => {
      const url = new URL(req.url ?? "", REDIRECT_URI);

      if (url.pathname !== CALLBACK_PATH) {
        res.writeHead(404);
        res.end("Not found");
        return;
      }

      const code = url.searchParams.get("code");
      const state = url.searchParams.get("state");
      const error = url.searchParams.get("error");

      if (error) {
        const errorDesc = url.searchParams.get("error_description") ?? error;
        res.writeHead(400, { "Content-Type": "text/html" });
        res.end(`<h1>Authorization failed</h1><p>${errorDesc}</p>`);
        handleError(new Error(`OAuth error: ${errorDesc}`));
        return;
      }

      if (!code || !state) {
        res.writeHead(400, { "Content-Type": "text/html" });
        res.end("<h1>Missing code or state</h1>");
        return;
      }

      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(
        "<h1>Authorization successful</h1><p>You can close this tab and return to your terminal.</p>",
      );
      handleResult({ code, state });
    });

    server.on("error", (err) => {
      // Port in use or permission denied — fall back to stdin-only mode
      console.warn(
        `Callback server unavailable (${err.message}) — using manual paste mode only`,
      );
      server = null; // Don't try to close it later
    });

    server.listen(CALLBACK_PORT, CALLBACK_HOST, () => {
      console.log(`OAuth callback server listening on ${CALLBACK_HOST}:${CALLBACK_PORT}`);
    });

    // --- Mode 2: stdin paste (headless / SSH without port-forward) ---
    // Always active as a fallback — if the callback server wins, stdin is cleaned up.
    // This handles: SSH without port forwarding, headless servers, containers.
    console.log(
      "\nIf the browser didn't open, or you're on a remote machine without port forwarding:\n" +
        "  1. Open the auth URL above in your LOCAL browser\n" +
        "  2. Log in and authorize\n" +
        '  3. Your browser redirects to http://127.0.0.1:8484/callback?code=...&state=...\n' +
        '     and shows "connection refused" — that\'s expected\n' +
        "  4. Copy the FULL URL from your browser's address bar and paste it here:\n",
    );
    process.stdin.resume();
    stdinListener = (chunk: Buffer) => {
      const input = chunk.toString().trim();
      if (!input) return;

      try {
        const url = new URL(input);
        const code = url.searchParams.get("code");
        const state = url.searchParams.get("state");
        const error = url.searchParams.get("error");

        if (error) {
          const desc = url.searchParams.get("error_description") ?? error;
          handleError(new Error(`OAuth error: ${desc}`));
          return;
        }

        if (!code || !state) {
          console.error(
            "URL doesn't contain code and state params. Paste the full redirect URL:",
          );
          return;
        }

        handleResult({ code, state });
      } catch {
        console.error("Invalid URL. Paste the full redirect URL from your browser:");
      }
    };
    process.stdin.on("data", stdinListener);
  });
}

/**
 * Exchange the authorization code for access + refresh tokens.
 */
async function exchangeCodeForTokens(
  config: OAuthConfig,
  code: string,
  codeVerifier: string,
): Promise<StoredTokens> {
  const response = await fetch(config.tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      client_id: config.clientId,
      code,
      redirect_uri: REDIRECT_URI,
      code_verifier: codeVerifier,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Token exchange failed (${response.status}): ${text}`);
  }

  const data = (await response.json()) as {
    access_token: string;
    refresh_token?: string;
    expires_in?: number;
  };

  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    expiresAt: Date.now() + (data.expires_in ?? 300) * 1000,
  };
}

/**
 * Refresh the access token using the stored refresh token.
 */
async function refreshAccessToken(config: OAuthConfig): Promise<string> {
  const stored = readStoredTokens();
  if (!stored?.refreshToken) {
    // No refresh token — need to re-authorize
    return authorizeWithPKCE(config);
  }

  const response = await fetch(config.tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      client_id: config.clientId,
      refresh_token: stored.refreshToken,
    }),
  });

  if (!response.ok) {
    // Refresh failed — need to re-authorize
    clearStoredTokens();
    return authorizeWithPKCE(config);
  }

  const data = (await response.json()) as {
    access_token: string;
    refresh_token?: string;
    expires_in?: number;
  };

  const tokens: StoredTokens = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token ?? stored.refreshToken,
    expiresAt: Date.now() + (data.expires_in ?? 300) * 1000,
  };
  writeStoredTokens(tokens);
  tokenCache = { token: tokens.accessToken, expiresAt: tokens.expiresAt };
  return tokens.accessToken;
}

/**
 * Get a valid access token:
 *   1. Return cached token if still valid
 *   2. Try refresh token if expired
 *   3. Fall back to full PKCE authorization if refresh fails
 */
async function getAccessToken(): Promise<string> {
  // Return cached token if still valid (30s buffer for clock skew)
  if (tokenCache && Date.now() < tokenCache.expiresAt - 30000) {
    return tokenCache.token;
  }

  const config = readOAuthConfig();

  // Try stored tokens first
  const stored = readStoredTokens();
  if (stored && Date.now() < stored.expiresAt - 30000) {
    tokenCache = { token: stored.accessToken, expiresAt: stored.expiresAt };
    return stored.accessToken;
  }

  // Token expired — try refresh
  if (stored?.refreshToken) {
    try {
      return await refreshAccessToken(config);
    } catch {
      // Refresh failed — fall through to full authorization
    }
  }

  // No stored tokens or refresh failed — full PKCE authorization
  return authorizeWithPKCE(config);
}

/** Clear the in-memory token cache — used when a 401 is received. */
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
      const dataLines = event.split("\n").filter((l) => l.startsWith("data:"));
      if (dataLines.length === 0) continue;

      // SSE data: lines are concatenated with \n; strip "data:" prefix and leading space
      const data = dataLines.map((l) => l.slice(5).replace(/^ /, "")).join("\n");

      try {
        const parsed = JSON.parse(data);
        if (parsed.error) {
          throw new Error(`MCP error: ${parsed.error.message ?? JSON.stringify(parsed.error)}`);
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