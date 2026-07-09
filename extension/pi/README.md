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

Install as a pi package (clones the repo and reads `package.json` to find the extension):

```bash
pi install git:github.com/AlienResidents/remember@main
```

Or add to `.pi/agent/settings.json`:

```json
{
  "packages": [
    "git:github.com/AlienResidents/remember@main"
  ]
}
```

## State

State directory: `~/.pi/agent/state/remember/`
