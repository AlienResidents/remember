# REMEMBER Pi Extension

Pi coding agent extension that connects to the REMEMBER MCP server and registers its tools.

## Tools

| Tool | Description |
|------|-------------|
| `remember__search_memories` | Search memories by query |
| `remember__get_memory` | Get full memory details |
| `remember__list_memories` | Browse memories with filters |
| `remember__get_stale_memories` | Find stale memories |
| `remember__save_memory` | Save/update a memory |
| `remember__verify_memory` | Mark memory as verified |
| `remember__archive_memory` | Archive a memory |
| `remember__confirm_memory` | Confirm memory accuracy |
| `remember__refute_memory` | Refute memory accuracy |

## Configuration

Set the REMEMBER MCP URL via environment variable or `.pi/settings.json`:

```bash
export REMEMBER_MCP_URL="https://remember.cdd.net.au/mcp"
```

Or in `.pi/settings.json`:

```json
{
  "remember": {
    "mcpUrl": "https://remember.cdd.net.au/mcp"
  }
}
```

## Installation

Install from the git repo (clones the repo and uses the `extension/pi` subdirectory):

```bash
pi extension add https://github.com/AlienResidents/remember@main#extension/pi
```

Or add to `.pi/settings.json`:

```json
{
  "extensions": {
    "paths": ["https://github.com/AlienResidents/remember@main#extension/pi"]
  }
}
```

## State

State directory: `~/.pi/agent/state/remember/`
