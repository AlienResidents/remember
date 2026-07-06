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
        "dev_mode": False,
    }))

    os.environ["CONFIG_FILE"] = str(config_file)
    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://test:test@localhost/test"
    assert settings.jwt_secret == "yaml-secret"
    assert settings.dev_mode is False

    # Cleanup
    config_file.unlink()
    config_dir.rmdir()


def test_settings_validation():
    """Test settings validation."""
    from pydantic import ValidationError

    # JWT secret too short
    with pytest.raises(ValidationError):
        Settings(jwt_secret="ab")


def test_settings_auth_config():
    """Test auth configuration parsing."""
    settings = Settings()
    auth_config = settings.get_auth_config()

    # Should have dev mode enabled by default
    assert "dev" in auth_config
    assert auth_config["dev"]["enabled"] is True


def test_settings_database_url():
    """Test database URL handling."""
    # SQLite (default)
    settings = Settings()
    assert "sqlite" in settings.database_url

    # PostgreSQL
    settings = Settings(database_url="postgresql+asyncpg://localhost/test")
    assert "postgresql" in settings.database_url
