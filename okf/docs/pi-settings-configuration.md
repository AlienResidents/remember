---
type: Documentation
description: "Pi Settings Configuration"
resource: docs/pi-settings-configuration.md
timestamp: 2026-07-10T02:44:32Z
---

# pi-settings-configuration

Source path: `docs/pi-settings-configuration.md`

## Content

# Pi Settings Configuration

The `~/.pi/agent/settings.json` file configures the pi coding agent.

## Key Sections

### Packages

Use object form with `source` and resource filters:

```json
{
  "packages": [
    {
      "source": "git:github.com/AlienResidents/remember@main",
      "extensions": ["extension/pi/index.ts"]
    }
  ]
}
```

### Extensions

Array of paths to extension directories:

```json
{
  "extensions": ["~/git/github/alienresidents/coding-agent-config/pi/extensions"]
}
```

### Skills

Array of paths to skill directories:

```json
{
  "skills": ["~/.pi/local/skills", "~/git/github/alienresidents/coding-agent-config/skills"]
}
```

### MCP Servers

Configure MCP servers under `mcp.servers`:

```json
{
  "mcp": {
    "servers": {
      "slack": {
        "transport": "http",
        "url": "https://mcp.slack.com/mcp",
        "auth": "oauth",
        "clientId": "..."
      }
    }
  }
}
```

### Compaction

Context compaction settings for long sessions:

```json
{
  "compaction": {
    "enabled": true,
    "reserveTokens": 128000,
    "keepRecentTokens": 20000
  }
}
```

## Installation Commands

```bash
# Install a package
pi install git:github.com/AlienResidents/remember@main

# Update a package
pi update git:github.com/AlienResidents/remember@main

# Update all packages
pi update --all
```

## Notes

- Package clones to `~/.pi/agent/git/<host>/<path>`
- After package changes, run `pi update` then `/reload`
- Extensions use `console.log` for logging (no `ctx.log`)
- `pi config` opens TUI to enable/disable resources (may timeout)
- The remember extension requires the remember MCP server to be configured and running
