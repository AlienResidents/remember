---
type: Infrastructure
description: "# REMEMBER Server - Docker Dockerfile"
resource: server/Dockerfile
timestamp: 2026-07-09T14:09:53Z
---

# Dockerfile

Source path: `server/Dockerfile`

## Content

```text
# REMEMBER Server - Docker Dockerfile
# Compatible with Podman (buildah-compatible)

# Build stage
FROM python:3.14-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and README for dependency installation
COPY server/pyproject.toml README.md .

# Install dependencies
RUN pip install --no-cache-dir --prefix=/install .

# Runtime stage
FROM python:3.14-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r remember && useradd -r -g remember remember

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /install /usr/local

# Copy application code
COPY server/remember/ ./remember/
COPY server/alembic.ini ./
COPY server/alembic/ ./alembic/

# Set ownership
RUN chown -R remember:remember /app

# Switch to non-root user
USER remember

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/healthz')" || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "-m", "uvicorn", "remember.server:mcp.app", "--host", "0.0.0.0", "--port", "8000"]

```
