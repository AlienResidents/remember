"""REMEMBER FastMCP server."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from remember.config import settings
from remember.db import init_db, close_db
from remember.tools import (
    search_memories,
    save_memory,
    get_memory,
    list_memories,
    get_stale_memories,
    verify_memory,
    archive_memory,
    confirm_memory,
    refute_memory,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "remember",
    instructions="Team memory system for collaborative knowledge sharing.",
)


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Server lifespan handler."""
    logger.info("Starting REMEMBER server...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down REMEMBER server...")
    await close_db()
    logger.info("Server shut down")


mcp.lifespan = server_lifespan


@mcp.tool()
async def healthcheck() -> dict:
    """Check server health."""
    return {"status": "healthy", "version": "0.1.0"}


# Expose the ASGI app for uvicorn (module:app pattern)
# Disable host origin protection to allow Traefik to forward requests
app = mcp.http_app(host_origin_protection=False)


async def healthz(request: Request):
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "version": "0.1.0"})


app.routes.append(Route("/healthz", healthz))


def main():
    """Run the server."""
    import uvicorn

    logger.info(f"Starting REMEMBER server on {settings.server.host}:{settings.server.port}")
    uvicorn.run(
        "remember.server:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.env == "development",
    )


if __name__ == "__main__":
    main()
