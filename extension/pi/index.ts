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
 *   ~/.pi/agent/state/remember/ — stores connection state and cached
 *   tool lists.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

/**
 * Extension factory. Called once when pi loads this extension.
 */
export default function rememberExtension(pi: ExtensionAPI, ctx: ExtensionContext) {
  const name = "remember";
  const label = "REMEMBER";
  const baseUrl = process.env.REMEMBER_MCP_URL || "https://remember.cdd.net.au/mcp";

  ctx.log.info(`${label} extension loaded (MCP URL: ${baseUrl})`);

  // Register REMEMBER as an MCP server via the mcp extension's
  // connection manager. The mcp extension handles JSON-RPC transport,
  // tool discovery, and error recovery — we just need to register the
  // server config and the tools will appear automatically.
  //
  // If the mcp extension isn't available (e.g. custom pi builds),
  // fall back to a direct HTTP fetch for tool discovery.
  try {
    // Attempt to register via the mcp extension's API if available.
    // The mcp extension exposes `registerServer` on the pi API.
    const mcpApi = (pi as any).mcp as { registerServer?: (config: any) => void } | undefined;
    if (mcpApi?.registerServer) {
      mcpApi.registerServer({
        name,
        transport: "http" as const,
        url: baseUrl,
        auth: "none" as const,
        enabled: true,
      });
      ctx.log.info(`${label} registered via mcp extension`);
      return;
    }
  } catch {
    // Fall through to direct registration
  }

  // Direct tool registration — used when the mcp extension isn't
  // available or when we want to override the default tool names.
  registerDirectTools(pi, name, label, baseUrl);
}

/**
 * Register REMEMBER tools directly via pi.registerTool().
 *
 * This is the fallback path when the mcp extension isn't available.
 * It uses a simple HTTP+JSON-RPC client to call the REMEMBER MCP
 * server directly.
 */
function registerDirectTools(pi: ExtensionAPI, name: string, label: string, baseUrl: string) {
  const prefix = `remember__`;

  // Tool definitions — mirrors the REMEMBER MCP tool surface.
  const tools = [
    {
      name: `${prefix}search_memories`,
      label: `${label}: Search Memories`,
      description: "Search memories by full-text query. Returns ranked metadata (no body).",
      promptSnippet: "Search memories for: ",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "Search query" },
          types: { type: "array", items: { type: "string" }, description: "Filter by type (project, reference)" },
          tags: { type: "array", items: { type: "string" }, description: "Filter by tags" },
          limit: { type: "number", description: "Max results", default: 10 },
        },
        required: ["query"],
      },
    },
    {
      name: `${prefix}get_memory`,
      label: `${label}: Get Memory`,
      description: "Get full memory including body, history count, and confirmations.",
      promptSnippet: "Get memory: ",
      parameters: {
        type: "object",
        properties: {
          id: { type: "string", description: "Memory ID" },
          user_id: { type: "string", description: "User ID for access logging" },
        },
        required: ["id"],
      },
    },
    {
      name: `${prefix}list_memories`,
      label: `${label}: List Memories`,
      description: "Browse memories with pagination and filters.",
      promptSnippet: "List memories",
      parameters: {
        type: "object",
        properties: {
          owner: { type: "string", description: "Filter by owner" },
          type: { type: "string", description: "Filter by type" },
          tag: { type: "string", description: "Filter by tag" },
          status: { type: "string", description: "Filter by status", default: "active" },
          updated_since: { type: "string", description: "ISO 8601 timestamp" },
          limit: { type: "number", description: "Page size", default: 20 },
          offset: { type: "number", description: "Pagination offset", default: 0 },
        },
      },
    },
    {
      name: `${prefix}get_stale_memories`,
      label: `${label}: Get Stale Memories`,
      description: "Return memories older than the threshold (default 90 days).",
      promptSnippet: "Find stale memories",
      parameters: {
        type: "object",
        properties: {
          threshold_days: { type: "number", description: "Days before considered stale", default: 90 },
        },
      },
    },
    {
      name: `${prefix}save_memory`,
      label: `${label}: Save Memory`,
      description: "Save or update a memory. Owner-only write.",
      promptSnippet: "Save memory: ",
      parameters: {
        type: "object",
        properties: {
          name: { type: "string", description: "Memory name (unique per owner)" },
          type: { type: "string", description: "Memory type (project or reference)" },
          description: { type: "string", description: "Brief description" },
          body: { type: "string", description: "Full markdown content" },
          owner_id: { type: "string", description: "Owner user ID" },
          tags: { type: "array", items: { type: "string" }, description: "Tags" },
          import_source: { type: "string", description: "Import source identifier" },
        },
        required: ["name", "type", "description", "body", "owner_id"],
      },
    },
    {
      name: `${prefix}verify_memory`,
      label: `${label}: Verify Memory`,
      description: "Mark a memory as verified. Owner-only.",
      promptSnippet: "Verify memory: ",
      parameters: {
        type: "object",
        properties: {
          memory_id: { type: "string", description: "Memory ID" },
          user_id: { type: "string", description: "User ID" },
        },
        required: ["memory_id", "user_id"],
      },
    },
    {
      name: `${prefix}archive_memory`,
      label: `${label}: Archive Memory`,
      description: "Archive a memory. Owner-only.",
      promptSnippet: "Archive memory: ",
      parameters: {
        type: "object",
        properties: {
          memory_id: { type: "string", description: "Memory ID" },
          user_id: { type: "string", description: "User ID" },
        },
        required: ["memory_id", "user_id"],
      },
    },
    {
      name: `${prefix}confirm_memory`,
      label: `${label}: Confirm Memory`,
      description: "Confirm a memory's accuracy. Any user can confirm.",
      promptSnippet: "Confirm memory: ",
      parameters: {
        type: "object",
        properties: {
          memory_id: { type: "string", description: "Memory ID" },
          user_id: { type: "string", description: "User ID" },
          note: { type: "string", description: "Confirmation note" },
        },
        required: ["memory_id", "user_id"],
      },
    },
    {
      name: `${prefix}refute_memory`,
      label: `${label}: Refute Memory`,
      description: "Refute a memory's accuracy. Any user can refute.",
      promptSnippet: "Refute memory: ",
      parameters: {
        type: "object",
        properties: {
          memory_id: { type: "string", description: "Memory ID" },
          user_id: { type: "string", description: "User ID" },
          reason: { type: "string", description: "Reason for refutation" },
        },
        required: ["memory_id", "user_id", "reason"],
      },
    },
  ];

  for (const tool of tools) {
    pi.registerTool({
      name: tool.name,
      label: tool.label,
      description: tool.description,
      promptSnippet: tool.promptSnippet,
      parameters: tool.parameters,
      async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
        // Call the REMEMBER MCP server via HTTP JSON-RPC.
        const result = await callRememberTool(tool.name, params, ctx);
        return {
          content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
          details: { server: "remember", tool: tool.name },
        };
      },
    });
  }

  ctx.log.info(`${label} extension loaded with ${tools.length} tools`);
}

/**
 * Call a REMEMBER MCP tool via HTTP JSON-RPC.
 */
async function callRememberTool(
  toolName: string,
  params: Record<string, unknown>,
  _ctx: ExtensionContext,
): Promise<Record<string, unknown>> {
  const baseUrl = process.env.REMEMBER_MCP_URL || "https://remember.cdd.net.au/mcp";
  const sessionId = generateSessionId();

  const jsonRpcRequest = {
    jsonrpc: "2.0",
    id: sessionId,
    method: "tools/call",
    params: {
      name: toolName.replace("remember__", ""),
      arguments: params,
    },
  };

  const response = await fetch(baseUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(jsonRpcRequest),
  });

  if (!response.ok) {
    throw new Error(`REMEMBER MCP error: ${response.status} ${response.statusText}`);
  }

  const result = await response.json();
  if (result.error) {
    throw new Error(`REMEMBER MCP error: ${result.error.message}`);
  }

  return result.result ?? {};
}

/**
 * Generate a unique session ID for JSON-RPC requests.
 */
function generateSessionId(): string {
  return `remember-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}
