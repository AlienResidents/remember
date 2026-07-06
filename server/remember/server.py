"""REMEMBER FastMCP server."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from remember.config import settings
from remember.db import init_db, close_db

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


def main():
    """Run the server."""
    import uvicorn

    logger.info(f"Starting REMEMBER server on {settings.server.host}:{settings.server.port}")
    uvicorn.run(
        "remember.server:mcp.app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.env == "development",
    )


if __name__ == "__main__":
    main()
