---
type: Source Code
description: "Tests for CLI tool."
resource: server/tests/test_cli.py
timestamp: 2026-07-10T02:44:34Z
---

# test cli

Source path: `server/tests/test_cli.py`

## Content

```python
"""Tests for CLI tool."""

import json
import tempfile
from pathlib import Path

import pytest

from remember.cli import main


def test_cli_import_dry_run():
    """Test CLI import in dry-run mode."""
    memories = [
        {
            "name": "test-memory",
            "type": "project",
            "description": "A test memory",
            "body": "# Test\n\nThis is a test memory.",
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(memories, f)
        f.flush()

        import subprocess
        result = subprocess.run(
            ["python", "-m", "remember.cli", "import", f.name, "--server-url", "http://localhost:8000", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "validated" in result.stdout.lower()

        Path(f.name).unlink()


def test_cli_export():
    """Test CLI export."""
```

*…truncated — full source at `server/tests/test_cli.py`*
