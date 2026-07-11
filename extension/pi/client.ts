/**
 * MCP client for the REMEMBER server.
 *
 * The server runs in stateless_http mode (no in-memory sessions), so each
 * request is standalone — any pod can serve any request. This lets the
 * server scale horizontally behind a load balancer.
 *
 * Auth: OAuth 2.0 Device Authorization Grant (RFC 8628) + PKCE.
 *   - Public client (no secret — desktop/CLI apps can't keep secrets)
 *   - PKCE S256 required by Keycloak (additional security on top of device flow)
 *   - No callback server needed — user opens a URL on ANY device
 *   - Extension polls the token endpoint until login completes
 *   - Tokens (access + refresh) cached in ~/.pi/agent/auth.json
 *   - Automatic refresh on expiry; re-authorize if refresh fails
 *
 * This is the same pattern used by `aws sso login`, `gh auth login`, etc.
 * Works in headless environments, SSH sessions, and inside TUIs (no stdin
 * needed — just prints a URL and polls).
 *
 * Identity: the JWT `sub` claim IS the user's Keycloak UUID. The server
 * reads it directly — no client_user_mapping needed.
 */

import { readFileSync, writeFileSync, existsSync, chmodSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";
import { randomBytes, createHash } from "node:crypto";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const AUTH_KEY = "remember-mcp";
const SCOPES = "openid profile email offline_access";

// L5: Timeout for all outbound HTTP calls (ms) — prevents indefinite hangs
// if Keycloak is unreachable/blackholed.
const FETCH_TIMEOUT = 10_000;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface OAuthConfig {
  clientId: string;
  tokenUrl: string;
  deviceAuthUrl: string;
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

function base64UrlEncode(buffer: Buffer): string {
  return buffer.toString("base64url");
}

function generateCodeVerifier(): string {
  return base64UrlEncode(randomBytes(32));
}

function generateCodeChallenge(verifier: string): string {
  return base64UrlEncode(createHash("sha256").update(verifier).digest());
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
  const authPath = getAuthPath();
  writeFileSync(authPath, JSON.stringify(data, null, 2) + "\n", { mode: 0o600 });
  // Ensure 0600 even if the file already existed (mode only applies on creation)
  chmodSync(authPath, 0o600);
}

function readOAuthConfig(): OAuthConfig {
  const auth = readAuthFile();
  const entry = auth[AUTH_KEY] as Partial<OAuthConfig> | undefined;
  if (!entry) {
    throw new Error(
      `No "${AUTH_KEY}" entry in ~/.pi/agent/auth.json. ` +
        `Expected: { clientId, tokenUrl, deviceAuthUrl }`,
    );
  }
  if (!entry.clientId || !entry.tokenUrl || !entry.deviceAuthUrl) {
    throw new Error(
      `"${AUTH_KEY}" entry missing required fields (clientId, tokenUrl, deviceAuthUrl)`,
    );
  }
  return {
    clientId: entry.clientId,
    tokenUrl: entry.tokenUrl,
    deviceAuthUrl: entry.deviceAuthUrl,
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
// M4: Single-flight — dedup concurrent refresh/device-flow calls.
// If two tool calls see the token as expired simultaneously, both would start
// a refresh (or worse, two device flows). This shared Promise ensures only
// one refresh runs at a time; concurrent callers await the same result.
let refreshInFlight: Promise<string> | null = null;

function openBrowser(url: string): void {
  // Defense-in-depth: validate URL scheme before passing to any process.
  // The URL comes from Keycloak's device authorization response
  // (verification_uri_complete). If the auth endpoint is compromised or
  // MITM'd, a malicious URL could contain shell metacharacters. On Windows,
  // `cmd /c start` interprets `&` as a command separator — a URL like
  // `https://evil/?x=1&calc.exe` would execute `calc.exe`.
  // Reject anything that isn't http:// or https://.
  if (!/^https?:\/\//i.test(url)) {
    return;
  }

  const platform = process.platform;
  let cmd: string;
  let args: string[];

  if (platform === "darwin") {
    cmd = "open";
    args = [url];
  } else if (platform === "win32") {
    // Avoid `cmd /c start` — cmd.exe is a shell and would interpret
    // metacharacters in the URL. rundll32 with url.dll,FileProtocolHandler
    // opens the URL in the default browser without shell interpretation.
    cmd = "rundll32";
    args = ["url.dll,FileProtocolHandler", url];
  } else {
    cmd = "xdg-open";
    args = [url];
  }

  try {
    spawn(cmd, args, { detached: true, stdio: "ignore" }).unref();
  } catch {
    // Ignore — user can open manually
  }
}

/**
 * Run the OAuth 2.0 Device Authorization Grant flow (RFC 8628):
 *   1. POST to device authorization endpoint (with PKCE)
 *   2. Display the verification URL + user code
 *   3. Open browser if possible
 *   4. Poll the token endpoint until login completes
 *   5. Store tokens in auth.json
 */
async function authorizeWithDeviceFlow(config: OAuthConfig): Promise<string> {
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);

  // Step 1: Request device authorization
  const deviceResponse = await fetch(config.deviceAuthUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: config.clientId,
      code_challenge: codeChallenge,
      code_challenge_method: "S256",
      scope: SCOPES, // L1: actually request the scopes we declared
    }),
    signal: AbortSignal.timeout(FETCH_TIMEOUT), // L5
  });

  if (!deviceResponse.ok) {
    const text = await deviceResponse.text();
    throw new Error(`Device authorization failed (${deviceResponse.status}): ${text}`);
  }

  const deviceData = (await deviceResponse.json()) as {
    device_code: string;
    user_code: string;
    verification_uri: string;
    verification_uri_complete: string;
    expires_in: number;
    interval: number;
  };

  // Step 2: Display the verification URL + user code
  console.log("\n=== OAuth Device Authorization Required ===");
  console.log("Open this URL in your browser to log in:\n");
  console.log(deviceData.verification_uri_complete);
  console.log(
    `\nOr go to ${deviceData.verification_uri} and enter code: ${deviceData.user_code}`,
  );
  console.log(`\nYou have ${deviceData.expires_in} seconds to complete login.`);

  // Step 3: Open browser if possible (no-op on headless)
  openBrowser(deviceData.verification_uri_complete);

  // Step 4: Poll for tokens
  console.log("\nWaiting for login...");

  const pollInterval = (deviceData.interval ?? 5) * 1000;
  const expiry = Date.now() + (deviceData.expires_in ?? 120) * 1000;

  while (Date.now() < expiry) {
    await new Promise((resolve) => setTimeout(resolve, pollInterval));

    const tokenResponse = await fetch(config.tokenUrl, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "urn:ietf:params:oauth:grant-type:device_code",
        client_id: config.clientId,
        device_code: deviceData.device_code,
        code_verifier: codeVerifier,
      }),
      signal: AbortSignal.timeout(FETCH_TIMEOUT), // L5
    });

    const tokenData = (await tokenResponse.json()) as {
      access_token?: string;
      refresh_token?: string;
      expires_in?: number;
      error?: string;
      error_description?: string;
    };

    if (tokenResponse.ok && tokenData.access_token) {
      // Success!
      const tokens: StoredTokens = {
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        expiresAt: Date.now() + (tokenData.expires_in ?? 300) * 1000,
      };
      writeStoredTokens(tokens);
      tokenCache = { token: tokens.accessToken, expiresAt: tokens.expiresAt };
      console.log("Login successful!\n");
      return tokens.accessToken;
    }

    if (tokenData.error === "authorization_pending") {
      process.stdout.write(".");
      continue;
    }
    if (tokenData.error === "slow_down") {
      // Back off by one interval
      await new Promise((resolve) => setTimeout(resolve, pollInterval));
      continue;
    }

    // Real error (expired, denied, etc.)
    throw new Error(
      `Device flow error: ${tokenData.error} — ${tokenData.error_description ?? ""}`,
    );
  }

  throw new Error("Device authorization expired before login completed");
}

/**
 * Refresh the access token using the stored refresh token.
 */
async function refreshAccessToken(config: OAuthConfig): Promise<string> {
  const stored = readStoredTokens();
  if (!stored?.refreshToken) {
    // No refresh token — need to re-authorize
    return authorizeWithDeviceFlow(config);
  }

  const response = await fetch(config.tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      client_id: config.clientId,
      refresh_token: stored.refreshToken,
    }),
    signal: AbortSignal.timeout(FETCH_TIMEOUT), // L5
  });

  if (!response.ok) {
    // Refresh failed — clear stored tokens and surface the error.
    // Do NOT fall back to authorizeWithDeviceFlow() inline: that polls
    // Keycloak for up to 120s waiting for browser login, which hangs
    // headless tool calls until pi's watchdog kills them at ~30s.
    // The user must re-authenticate explicitly via the login tool/command.
    clearStoredTokens();
    throw new Error(
      `OAuth refresh failed (${response.status}). ` +
        `Re-authentication required — run: pi remember login`,
    );
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
 *   2. Try stored token if still valid
 *   3. Try refresh token if expired
 *   4. Fall back to device flow authorization if refresh fails
 *
 * M4: Single-flight — if a refresh/device-flow is already in progress,
 * concurrent callers await the same promise instead of starting a second
 * flow. Without this, two tool calls seeing an expired token simultaneously
 * could start two device flows (confusing for the user — two browser tabs)
 * or race on the auth.json file.
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

  // M4: Single-flight — if a refresh/device-flow is already in progress,
  // await the same promise instead of starting a second one.
  if (refreshInFlight) {
    return refreshInFlight;
  }

  // Token expired — try refresh. If refresh fails (or there's no refresh
  // token), throw an auth error. Do NOT fall back to authorizeWithDeviceFlow()
  // inline: that polls Keycloak for up to 120s waiting for browser login,
  // which hangs headless tool calls until pi's watchdog kills them at ~30s.
  // The user must re-authenticate explicitly via the login tool/command.
  refreshInFlight = (async () => {
    try {
      if (stored?.refreshToken) {
        return await refreshAccessToken(config);
      }
    } catch (e) {
      throw new Error(
        `Authentication required — refresh failed: ` +
          `${e instanceof Error ? e.message : String(e)}. ` +
          `Run: pi remember login`,
      );
    }
    throw new Error(
      `No refresh token available. Re-authentication required — ` +
        `run: pi remember login`,
    );
  })().finally(() => {
    refreshInFlight = null;
  });

  return refreshInFlight;
}

/**
 * Clear the token cache — used when a 401 is received.
 *
 * M3: Also invalidates the stored token's expiry in auth.json. Without this,
 * getAccessToken() would re-read the same (server-rejected) token from disk
 * and the 401 retry would be inert — same token, same 401.
 *
 * Setting expiresAt=0 forces getAccessToken() to treat the stored token as
 * expired and attempt a refresh (or device flow if refresh also fails).
 */
export function clearTokenCache(): void {
  tokenCache = null;
  const stored = readStoredTokens();
  if (stored) {
    stored.expiresAt = 0;
    writeStoredTokens(stored);
  }
}

/**
 * Explicit login entry point — runs the OAuth device authorization flow.
 *
 * This is the ONLY place authorizeWithDeviceFlow() should be called from.
 * Tool calls (callTool → getAccessToken) throw auth errors instead of
 * falling back to device flow inline, because inline device flow polls
 * for 120s and hangs headless sessions. Users trigger this deliberately.
 *
 * Returns the new access token on success.
 */
export async function login(): Promise<string> {
  const config = readOAuthConfig();
  tokenCache = null; // invalidate cache so the new token takes effect
  return authorizeWithDeviceFlow(config);
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
      signal: AbortSignal.timeout(FETCH_TIMEOUT), // L5
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

      const data = dataLines.map((l) => l.slice(5).replace(/^ /, "")).join("\n");

      try {
        const parsed = JSON.parse(data);
        if (parsed.error) {
          throw new Error(`MCP error: ${parsed.error.message ?? JSON.stringify(parsed.error)}`);
        }
        return parsed.result ?? parsed;
      } catch (e) {
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