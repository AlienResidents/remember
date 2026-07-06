"""Database migration utilities."""

import asyncio
import sys
from pathlib import Path

from alembic.config import Config
from alembic import command


def run_migrations(direction: str = "upgrade", revision: str = "head"):
    """Run Alembic migrations.

    Args:
        direction: 'upgrade' or 'downgrade'
        revision: Target revision (default: 'head')
    """
    alembic_cfg = Config("alembic.ini")
    getattr(command, direction)(alembic_cfg, revision)


def main():
    """CLI entry point for migrations."""
    if len(sys.argv) < 2:
        print("Usage: remember-migrate [upgrade|downgrade] [revision]")
        sys.exit(1)

    direction = sys.argv[1]
    revision = sys.argv[2] if len(sys.argv) > 2 else "head"

    run_migrations(direction, revision)


if __name__ == "__main__":
    main()
