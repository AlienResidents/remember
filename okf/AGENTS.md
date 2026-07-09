---
type: Documentation
description: "AGENTS.md — AI Agent Guidelines"
resource: AGENTS.md
timestamp: 2026-07-09T14:09:52Z
---

# AGENTS

Source path: `AGENTS.md`

## Content

# AGENTS.md — AI Agent Guidelines

## Before You Start

1. **Read `okf/index.md`** — Understand the knowledge bundle structure
2. **Check `okf/detect-drift.bash`** — Run drift detection before committing
3. **Follow OKF conventions** — Every source file needs a matching concept

## OKF Knowledge Bundle

The `okf/` directory is the system of record. Before modifying source code:

1. Check if a concept already exists for the file/directory
2. If adding new source files, author corresponding OKF concepts
3. Run `bash okf/detect-drift.bash` to verify no drift

## Quick Reference

| Source | OKF Concept |
|--------|-------------|
| `server/remember/tools/*.py` | `okf/tools/<name>.md` |
| `server/remember/auth/*.py` | `okf/auth/<name>.md` |
| `server/remember/webui/*` | `okf/webui.md` |
| `extension/<name>/` | `okf/extension/<name>.md` |

## Drift Detection

```bash
# Run before committing
bash okf/detect-drift.bash

# If drift found, fix it:
#   - Author missing concepts, OR
#   - Remove orphan concepts
```

## Bash Standards

- Never use `IFS`
- Use `set -euo pipefail`
- Quote variables
- Use `[[ ]]` for conditionals
- Run `shellcheck` before committing
