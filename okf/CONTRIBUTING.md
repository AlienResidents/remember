---
type: Documentation
description: "Contributing to REMEMBER"
resource: CONTRIBUTING.md
timestamp: 2026-07-09T01:43:38Z
---

# CONTRIBUTING

Source path: `CONTRIBUTING.md`

## Content

# Contributing to REMEMBER

Thank you for your interest in contributing to REMEMBER! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you agree to uphold this code.

## How to Contribute

### Reporting Bugs

- Use the GitHub issue tracker
- Include as much detail as possible: steps to reproduce, expected behavior, actual behavior
- Include version numbers and environment details

### Suggesting Enhancements

- Use the GitHub issue tracker
- Explain the enhancement and why it would be useful
- Consider the scope and impact

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Run tests and linting
5. Commit with clear, descriptive messages
6. Push to your fork
7. Open a Pull Request against `main`

#### Commit Message Format

```
TYPE(scope): Brief description

Detailed description if needed.

👽 Directed by <name> <<email>>
Authored by <model>
```

Types:
- `INIT` — Initial structure
- `FEAT` — New feature
- `FIX` — Bug fix
- `DOCS` — Documentation changes
- `STYLE` — Code style changes (formatting, etc.)
- `REFACT` — Refactoring
- `TEST` — Adding or updating tests
- `CHORE` — Maintenance tasks

#### PR Checklist

- [ ] Changes are tested
- [ ] Code follows style guidelines
- [ ] Documentation is updated if needed
- [ ] Commits are squashed into logical units
- [ ] PR description explains what and why

## Development Setup

### Prerequisites

- Python 3.11+
- Postgres 16+ with pgvector extension
- Podman or Docker (for containerized dev)

### Local Development

```bash
# Clone the repo
git clone https://github.com/AlienResidents/remember.git
cd remember

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e server[dev]

# Run migrations
cd server
alembic upgrade head

# Start the server (dev mode, skips auth)
python -m remember.server --config config.dev.yaml
```

### Running Tests

```bash
cd server
pytest
```

### Linting

```bash
cd server
ruff check .
ruff format --check .
```

## Architecture Overview

See [docs/design.md](docs/design.md) for the full architecture document.

Key components:
- **Server** — FastMCP application for memory storage/retrieval
- **Database** — Postgres with pgvector for future semantic search
- **Auth** — Pluggable identity providers (GitHub, API keys, Tailscale, etc.)
- **CLI** — Command-line tool for import/export and management

## Contact

- GitHub Issues: [https://github.com/AlienResidents/remember/issues](https://github.com/AlienResidents/remember/issues)
- Discussions: [https://github.com/AlienResidents/remember/discussions](https://github.com/AlienResidents/remember/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
