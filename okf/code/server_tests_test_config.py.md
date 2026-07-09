---
type: Source Code
description: "Tests for configuration."
resource: server/tests/test_config.py
timestamp: 2026-07-09T13:54:50Z
---

# test config

Source path: `server/tests/test_config.py`

## Content

```python
"""Tests for configuration."""

import os
from pathlib import Path

import pytest
import yaml

from remember.config import Settings


def test_settings_defaults():
    """Test settings with default values."""
    settings = Settings()
    assert settings.database_url == "sqlite+aiosqlite:///db.sqlite3"
    assert settings.jwt_secret == "change-me-in-production"
    assert settings.api_key is None
    assert settings.dev_mode is True


def test_settings_from_env(monkeypatch):
    """Test settings from environment variables."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("DEV_MODE", "false")

    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://user:pass@localhost/db"
    assert settings.jwt_secret == "test-secret"
    assert settings.dev_mode is False


def test_settings_from_yaml():
    """Test settings from YAML config file."""
    config_dir = Path(__file__).parent.parent / "test_config"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text(yaml.dump({
        "database_url": "postgresql+asyncpg://test:test@localhost/test",
        "jwt_secret": "yaml-secret",
```

*…truncated — full source at `server/tests/test_config.py`*
