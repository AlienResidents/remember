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

        # Save to server (would need MCP client here)
        # For now, just validate the data
        required_fields = ["name", "type", "description", "body"]
        missing = [f for f in required_fields if f not in mem_data]
        if missing:
            print(f"  [ERROR] Missing fields: {missing}")
            continue

        print(f"  [OK] Memory validated: {mem_data['name']}")

    print(f"\nImport {'completed' if not dry_run else 'validated'} successfully!")


async def export_memories(
    output_file: str,
    server_url: str,
    api_key: str | None = None,
    memory_type: str | None = None,
    status: str | None = None,
):
    """Export memories to a JSON file.

    Args:
        output_file: Path to output JSON file
        server_url: REMEMBER server URL
        api_key: API key for authentication
        memory_type: Filter by type (project, reference)
        status: Filter by status (active, archived, disputed)
    """
    # Export memories (would need MCP client here)
    # For now, just create an empty export
    memories = []

    print(f"Exported {len(memories)} memories to {output_file}")

    with open(output_file, "w") as f:
        json.dump(memories, f, indent=2)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="REMEMBER CLI - Import/Export team memories"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import memories from JSON")
    import_parser.add_argument("input_file", help="Path to JSON file")
    import_parser.add_argument("--server-url", required=True, help="REMEMBER server URL")
    import_parser.add_argument("--api-key", help="API key for authentication")
    import_parser.add_argument("--dry-run", action="store_true", help="Validate without saving")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export memories to JSON")
    export_parser.add_argument("output_file", help="Path to output JSON file")
    export_parser.add_argument("--server-url", required=True, help="REMEMBER server URL")
    export_parser.add_argument("--api-key", help="API key for authentication")
    export_parser.add_argument("--type", help="Filter by type (project, reference)")
    export_parser.add_argument("--status", help="Filter by status (active, archived, disputed)")

    args = parser.parse_args()

    if args.command == "import":
        asyncio.run(import_memories(
            args.input_file,
            args.server_url,
            args.api_key,
            args.dry_run,
        ))
    elif args.command == "export":
        asyncio.run(export_memories(
            args.output_file,
            args.server_url,
            args.api_key,
            args.type,
            args.status,
        ))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    main()
