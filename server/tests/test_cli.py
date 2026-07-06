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
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "remember.cli", "export", f.name, "--server-url", "http://localhost:8000"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert Path(f.name).exists()
        Path(f.name).unlink()


def test_cli_help():
    """Test CLI help output."""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "remember.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "import" in result.stdout
    assert "export" in result.stdout


def test_cli_no_command():
    """Test CLI with no command shows help."""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "remember.cli"],
        capture_output=True,
        text=True,
    )
    # Should show help or exit with error
    assert result.returncode in [0, 1]
