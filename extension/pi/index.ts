/**
 * REMEMBER Pi Extension
 *
 * Connects to the REMEMBER MCP server and registers its tools in pi.
 *
 * Auth: OAuth 2.0 Device Authorization Grant (RFC 8628) + PKCE.
 *   - Public client (no secret — desktop/CLI apps can't keep secrets)
 *   - PKCE S256 required by Keycloak (additional security)
 *   - No callback server — user opens a URL on ANY device
 *   - Extension polls the token endpoint until login completes
 *   - Tokens (access + refresh) cached in ~/.pi/agent/auth.json
 *   - Automatic refresh on expiry; re-authorize if refresh fails
 *
 * This is the same pattern used by `aws sso login`, `gh auth login`, etc.
 * Works in headless environments, SSH sessions, and inside TUIs.
 *
 * The server runs in stateless_http mode — each tools/call is standalone,
 * no initialize handshake or session tracking needed.
 *
 * Identity resolution:
 *   The server reads the JWT `sub` claim (Keycloak user UUID) directly.
 *   The extension does NOT inject identity params — the server does not
 *   trust client-supplied identity. No client_user_mapping needed.
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
 */
export default function rememberExtension(pi: ExtensionAPI, _ctx: ExtensionContext) {
  const baseUrl = process.env.REMEMBER_MCP_URL || DEFAULT_URL;
  const client = new RememberMcpClient(baseUrl);

  console.log(`${LABEL} extension loaded (MCP URL: ${baseUrl})`);

  registerTools(pi, client);
}

// ---------------------------------------------------------------------------
// Tool definitions + registration
// ---------------------------------------------------------------------------

interface ToolDef {
  mcpName: string; // name on the MCP server (without prefix)
  label: string;
  description: string;
  promptSnippet: string;
  parameters: Record<string, unknown>;
  required: string[];
}

const TOOLS: ToolDef[] = [
  {
    mcpName: "search_memories",
    label: `${LABEL}: Search Memories`,
    description:
      "Search memories by full-text query. Returns ranked metadata (no body).",
    promptSnippet: "Search memories for: ",
    parameters: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" },
        types: {
          type: "array",
          items: { type: "string" },
          description: "Filter by type (project, reference)",
        },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Filter by tags",
        },
        limit: { type: "number", description: "Max results", default: 10 },
      },
    },
    required: ["query"],
  },
  {
    mcpName: "get_memory",
    label: `${LABEL}: Get Memory`,
    description:
      "Get full memory including body, history count, and confirmations.",
    promptSnippet: "Get memory: ",
    parameters: {
      type: "object",
      properties: {
        id: { type: "string", description: "Memory ID" },
      },
    },
    required: ["id"],
  },
  {
    mcpName: "list_memories",
    label: `${LABEL}: List Memories`,
    description: "Browse memories with pagination and filters.",
    promptSnippet: "List memories",
    parameters: {
      type: "object",
      properties: {
        type: { type: "string", description: "Filter by type" },
        tag: { type: "string", description: "Filter by tag" },
        status: { type: "string", description: "Filter by status", default: "active" },
        updated_since: { type: "string", description: "ISO 8601 timestamp" },
        limit: { type: "number", description: "Page size", default: 20 },
        offset: { type: "number", description: "Pagination offset", default: 0 },
      },
    },
    required: [],
  },
  {
    mcpName: "get_stale_memories",
    label: `${LABEL}: Get Stale Memories`,
    description: "Return memories older than the threshold (default 90 days).",
    promptSnippet: "Find stale memories",
    parameters: {
      type: "object",
      properties: {
        threshold_days: {
          type: "number",
          description: "Days before considered stale",
          default: 90,
        },
      },
    },
    required: [],
  },
  {
    mcpName: "save_memory",
    label: `${LABEL}: Save Memory`,
    description: "Save or update a memory. Owner-only write.",
    promptSnippet: "Save memory: ",
    parameters: {
      type: "object",
      properties: {
        name: { type: "string", description: "Memory name (unique per owner)" },
        type: { type: "string", description: "Memory type (project or reference)" },
        description: { type: "string", description: "Brief description" },
        body: { type: "string", description: "Full markdown content" },
        tags: { type: "array", items: { type: "string" }, description: "Tags" },
        import_source: { type: "string", description: "Import source identifier" },
      },
    },
    required: ["name", "type", "description", "body"],
  },
  {
    mcpName: "verify_memory",
    label: `${LABEL}: Verify Memory`,
    description: "Mark a memory as verified. Owner-only.",
    promptSnippet: "Verify memory: ",
    parameters: {
      type: "object",
      properties: {
        memory_id: { type: "string", description: "Memory ID" },
      },
    },
    required: ["memory_id"],
  },
  {
    mcpName: "archive_memory",
    label: `${LABEL}: Archive Memory`,
    description: "Archive a memory. Owner-only.",
    promptSnippet: "Archive memory: ",
    parameters: {
      type: "object",
      properties: {
        memory_id: { type: "string", description: "Memory ID" },
      },
    },
    required: ["memory_id"],
  },
  {
    mcpName: "confirm_memory",
    label: `${LABEL}: Confirm Memory`,
    description: "Confirm a memory's accuracy. Any user can confirm.",
    promptSnippet: "Confirm memory: ",
    parameters: {
      type: "object",
      properties: {
        memory_id: { type: "string", description: "Memory ID" },
        note: { type: "string", description: "Confirmation note" },
      },
    },
    required: ["memory_id"],
  },
  {
    mcpName: "refute_memory",
    label: `${LABEL}: Refute Memory`,
    description: "Refute a memory's accuracy. Any user can refute.",
    promptSnippet: "Refute memory: ",
    parameters: {
      type: "object",
      properties: {
        memory_id: { type: "string", description: "Memory ID" },
        reason: { type: "string", description: "Reason for refutation" },
      },
    },
    required: ["memory_id", "reason"],
  },
];

function registerTools(
  pi: ExtensionAPI,
  client: RememberMcpClient,
): void {
  for (const tool of TOOLS) {
    const toolName = `${PREFIX}${tool.mcpName}`;

    pi.registerTool({
      name: toolName,
      label: tool.label,
      description: tool.description,
      promptSnippet: tool.promptSnippet,
      parameters: {
        ...tool.parameters,
        required: tool.required,
      },
      async execute(_toolCallId, params, _signal, _onUpdate, _ctx) {
        // Identity is derived from the JWT on the server side.
        // The extension does NOT inject identity params.
        const result = await client.callTool(tool.mcpName, params);

        // Pass through MCP content blocks directly.
        // The remember server always returns text content.
        const content = (result.content ?? []).map((block) => {
          if (block.type === "text" && typeof block.text === "string") {
            return { type: "text" as const, text: block.text };
          }
          // Fallback for non-text blocks: stringify
          return {
            type: "text" as const,
            text: JSON.stringify(block),
          };
        });

        if (content.length === 0) {
          content.push({ type: "text", text: JSON.stringify(result) });
        }

        return {
          content,
          details: { server: "remember", tool: tool.mcpName, isError: result.isError },
        };
      },
    });
  }

  console.log(`${LABEL} extension registered ${TOOLS.length} tools`);
}