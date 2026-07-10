---
type: Source Code
description: "CLI tool for REMEMBER import/export."
resource: server/remember/cli.py
timestamp: 2026-07-10T02:44:33Z
---

# cli

Source path: `server/remember/cli.py`

## Content

```python
"""CLI tool for REMEMBER import/export."""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from remember.db import async_session_factory
from remember.models import Memory, User
from remember.tools import save_memory, list_memories


async def import_memories(
    input_file: str,
    server_url: str,
    api_key: str | None = None,
    dry_run: bool = False,
):
    """Import memories from a JSON file.

    Args:
        input_file: Path to JSON file with memories
        server_url: REMEMBER server URL
        api_key: API key for authentication
        dry_run: Don't actually save, just validate
    """
    # Load memories from file
    with open(input_file, "r") as f:
        memories_data = json.load(f)

    print(f"Loaded {len(memories_data)} memories from {input_file}")

    # Import each memory
    for i, mem_data in enumerate(memories_data, 1):
        print(f"Importing memory {i}/{len(memories_data)}: {mem_data.get('name', 'unknown')}")

        if dry_run:
            print(f"  [DRY RUN] Would import: {mem_data.get('name')}")
            continue
```

*…truncated — full source at `server/remember/cli.py`*
