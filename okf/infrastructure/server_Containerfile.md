---
type: Infrastructure
description: "# REMEMBER Server - Podman Containerfile"
resource: server/Containerfile
timestamp: 2026-07-09T01:43:39Z
---

# Containerfile

Source path: `server/Containerfile`

## Content

```text
# REMEMBER Server - Podman Containerfile
# Multi-stage build for minimal production image

# Build stage
FROM python:3.14-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and README for dependency installation
COPY pyproject.toml README.md .

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
COPY remember/ ./remember/
COPY webui/ ./webui/
COPY alembic.ini ./
COPY alembic/ ./alembic/

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
CMD ["python", "-m", "uvicorn", "remember.server:app", "--host", "0.0.0.0", "--port", "8000"]

```
