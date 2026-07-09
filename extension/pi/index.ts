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
 * The extension implements the MCP streamable HTTP transport directly:
 *   1. OAuth client_credentials → bearer token (cached, auto-refresh)
 *   2. MCP initialize handshake → capture Mcp-Session-Id
 *   3. tools/call → execute and return content
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
        user_id: { type: "string", description: "User ID for access logging" },
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
        owner: { type: "string", description: "Filter by owner" },
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
        owner_id: { type: "string", description: "Owner user ID" },
        tags: { type: "array", items: { type: "string" }, description: "Tags" },
        import_source: { type: "string", description: "Import source identifier" },
      },
    },
    required: ["name", "type", "description", "body", "owner_id"],
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
        user_id: { type: "string", description: "User ID" },
      },
    },
    required: ["memory_id", "user_id"],
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
        user_id: { type: "string", description: "User ID" },
      },
    },
    required: ["memory_id", "user_id"],
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
        user_id: { type: "string", description: "User ID" },
        note: { type: "string", description: "Confirmation note" },
      },
    },
    required: ["memory_id", "user_id"],
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
        user_id: { type: "string", description: "User ID" },
        reason: { type: "string", description: "Reason for refutation" },
      },
    },
    required: ["memory_id", "user_id", "reason"],
  },
];

function registerTools(pi: ExtensionAPI, client: RememberMcpClient): void {
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