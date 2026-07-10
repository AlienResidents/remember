"""Tests for configuration."""

import os
from pathlib import Path

import pytest

from remember.config import Settings


def test_settings_defaults(monkeypatch):
    """Test settings with default values (clear env overrides from conftest)."""
    monkeypatch.delenv("REMEMBER_AUTH__DEV_MODE", raising=False)
    settings = Settings()
    assert settings.database.url == "postgresql+asyncpg://localhost:5432/remember"
    assert settings.auth.dev_mode is False
    assert settings.server.host == "0.0.0.0"
    assert settings.server.port == 8000


def test_settings_from_env(monkeypatch):
    """Test settings from environment variables (nested via __ delimiter)."""
    monkeypatch.delenv("REMEMBER_AUTH__DEV_MODE", raising=False)
    monkeypatch.setenv("REMEMBER_DATABASE__URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("REMEMBER_AUTH__DEV_MODE", "true")
    monkeypatch.setenv("REMEMBER_SERVER__PORT", "9000")

    settings = Settings()
    assert settings.database.url == "postgresql+asyncpg://user:pass@localhost/db"
    assert settings.auth.dev_mode is True
    assert settings.server.port == 9000


def test_settings_database_url():
    """Test database URL handling."""
    # Default
    settings = Settings()
    assert "postgresql" in settings.database.url

    # Override via nested field
    settings = Settings()
    settings.database.url = "sqlite+aiosqlite:///test.sqlite3"
    assert "sqlite" in settings.database.url


def test_settings_auth_config(monkeypatch):
    """Test auth configuration."""
    monkeypatch.delenv("REMEMBER_AUTH__DEV_MODE", raising=False)
    settings = Settings()
    assert settings.auth.dev_mode is False
    assert settings.auth.keycloak_authority == ""
    assert settings.auth.keycloak_enabled is False


def test_settings_keycloak_enabled(monkeypatch):
    """Test keycloak_enabled property."""
    monkeypatch.delenv("REMEMBER_AUTH__DEV_MODE", raising=False)

    settings = Settings()
    # Not enabled by default (no authority)
    assert settings.auth.keycloak_enabled is False

    # Enabled when authority is set and dev_mode is False
    settings.auth.keycloak_authority = "https://keycloak.example.com"
    assert settings.auth.keycloak_enabled is True

    # Disabled when dev_mode is True
    settings.auth.dev_mode = True
    assert settings.auth.keycloak_enabled is False


def test_settings_keycloak_urls():
    """Test Keycloak URL construction."""
    settings = Settings()
    settings.auth.keycloak_authority = "https://kc.example.com"
    settings.auth.keycloak_realm = "myrealm"

    assert settings.auth.keycloak_jwks_url == (
        "https://kc.example.com/realms/myrealm/protocol/openid-connect/certs"
    )
    assert settings.auth.keycloak_issuer == "https://kc.example.com/realms/myrealm"