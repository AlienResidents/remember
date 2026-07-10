"""REMEMBER FastMCP server."""

import asyncio
import logging
from contextlib import asynccontextmanager

import jwt
from fastmcp import FastMCP, Context
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

import uuid as uuid_module
from datetime import datetime

from sqlalchemy import select

from remember.config import settings
from remember.db import init_db, close_db, async_session_factory
from remember.models import User
from remember.tools import (
    search_memories as _search_memories,
    save_memory as _save_memory,
    get_memory as _get_memory,
    list_memories as _list_memories,
    get_stale_memories as _get_stale_memories,
    verify_memory as _verify_memory,
    archive_memory as _archive_memory,
    confirm_memory as _confirm_memory,
    refute_memory as _refute_memory,
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


# --- MCP tool wrappers ---
# These wrap the underlying tool functions, hiding the `db` parameter
# and converting string IDs to UUIDs for the MCP schema.


@mcp.tool()
async def search_memories(
    query: str,
    types: list[str] | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
    ctx: Context | None = None,
) -> list[dict]:
    """Search memories by full-text query. Returns ranked metadata (no body)."""
    owner_id = await resolve_user_id(ctx)
    return await _search_memories(query=query, types=types, tags=tags, limit=limit, owner_id=owner_id)


@mcp.tool()
async def get_memory(id: str, ctx: Context | None = None) -> dict | None:
    """Get full memory including body, history count, and confirmations."""
    user_id = await resolve_user_id(ctx)
    return await _get_memory(
        memory_id=uuid_module.UUID(id),
        user_id=user_id,
    )


@mcp.tool()
async def list_memories(
    type: str | None = None,
    tag: str | None = None,
    status: str = "active",
    updated_since: str | None = None,
    limit: int = 50,
    offset: int = 0,
    ctx: Context | None = None,
) -> list[dict]:
    """Browse memories with pagination and filters."""
    owner_id = await resolve_user_id(ctx)
    return await _list_memories(
        owner_id=owner_id,
        type=type,
        tag=tag,
        status=status,
        updated_since=datetime.fromisoformat(updated_since) if updated_since else None,
        limit=limit + offset,
    )


@mcp.tool()
async def get_stale_memories(threshold_days: int = 90, ctx: Context | None = None) -> list[dict]:
    """Return memories older than the threshold (default 90 days)."""
    owner_id = await resolve_user_id(ctx)
    return await _get_stale_memories(threshold_days=threshold_days, owner_id=owner_id)


@mcp.tool()
async def save_memory(
    name: str,
    type: str,
    description: str,
    body: str,
    tags: list[str] | None = None,
    import_source: str | None = None,
    ctx: Context | None = None,
) -> dict:
    """Save or update a memory. Owner-only write."""
    owner_id = await resolve_user_id(ctx)
    return await _save_memory(
        name=name,
        type=type,
        description=description,
        body=body,
        owner_id=owner_id,
        tags=tags,
        import_source=import_source,
    )


@mcp.tool()
async def verify_memory(memory_id: str, ctx: Context | None = None) -> dict:
    """Mark a memory as verified. Owner-only."""
    user_id = await resolve_user_id(ctx)
    return await _verify_memory(
        memory_id=uuid_module.UUID(memory_id),
        user_id=user_id,
    )


@mcp.tool()
async def archive_memory(memory_id: str, ctx: Context | None = None) -> dict:
    """Archive a memory. Owner-only."""
    user_id = await resolve_user_id(ctx)
    return await _archive_memory(
        memory_id=uuid_module.UUID(memory_id),
        user_id=user_id,
    )


@mcp.tool()
async def confirm_memory(
    memory_id: str,
    note: str | None = None,
    ctx: Context | None = None,
) -> dict:
    """Confirm a memory's accuracy. Any user can confirm."""
    user_id = await resolve_user_id(ctx)
    return await _confirm_memory(
        memory_id=uuid_module.UUID(memory_id),
        user_id=user_id,
        note=note,
    )


@mcp.tool()
async def refute_memory(memory_id: str, reason: str, ctx: Context | None = None) -> dict:
    """Refute a memory's accuracy. Any user can refute."""
    user_id = await resolve_user_id(ctx)
    return await _refute_memory(
        memory_id=uuid_module.UUID(memory_id),
        user_id=user_id,
        reason=reason,
    )


# ---------------------------------------------------------------------------
# User identity resolution
# ---------------------------------------------------------------------------
# H1 fix: identity is derived EXCLUSIVELY from the JWT (via ctx).
# Client-supplied owner_id/user_id params are no longer accepted —
# the server does not trust the client for authorization decisions.
#
# The middleware extracts azp from the JWT, looks up client_user_mapping,
# and stashes auth_provider_id on request.state. This function reads that
# and resolves it to a UUID via get-or-create on the User table.
#
# The mapping value MUST be the Keycloak user's `sub` claim (the immutable
# OIDC subject identifier), NOT a username. The web UI also uses `sub` as
# provider_id, so both paths converge on the same User row.


async def get_or_create_user_by_provider_id(provider_id: str) -> uuid_module.UUID:
    """Get or create a User by Keycloak provider_id (the `sub` claim)."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(User).where(
                User.provider == "keycloak",
                User.provider_id == provider_id,
            )
        )
        user = result.scalar_one_or_none()
        if user:
            return user.id

        user = User(
            provider="keycloak",
            provider_id=provider_id,
            display_name=provider_id,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user.id


async def resolve_user_id(ctx: Context | None = None) -> uuid_module.UUID:
    """Resolve the authenticated user's UUID from the JWT via ctx.

    H1 fix: identity comes exclusively from the JWT azp claim (set by
    the middleware via client_user_mapping). Client-supplied identity
    strings are NOT accepted — the server does not trust the client.
    """
    if ctx is not None:
        try:
            request = ctx.request_context.request
        except Exception:
            request = None
        if request is not None:
            provider_id = getattr(request.state, "auth_provider_id", "")
            if provider_id:
                return await get_or_create_user_by_provider_id(provider_id)

    raise ValueError(
        "No user identity in JWT — configure REMEMBER_AUTH__CLIENT_USER_MAPPING"
    )


# Expose the ASGI app for uvicorn (module:app pattern).
# Disable host origin protection to allow Traefik to forward requests.
# stateless_http=True: create a fresh transport per request with no in-memory
# session tracking. This lets the server run behind a load balancer across
# multiple replicas — any pod can serve any request. Our tools are
# self-contained (each makes its own DB session), so stateful MCP sessions
# aren't needed.
app = mcp.http_app(host_origin_protection=False, stateless_http=True)


class _AuthError(Exception):
    """Raised when JWT validation fails."""



class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Validate bearer tokens via local JWT verification against Keycloak JWKS."""

    # PyJWKClient handles JWKS fetching, caching, and key selection by kid header
    _jwks_client: jwt.PyJWKClient | None = None

    @classmethod
    def _get_jwks_client(cls) -> jwt.PyJWKClient:
        if cls._jwks_client is None:
            cls._jwks_client = jwt.PyJWKClient(settings.auth.keycloak_jwks_url)
        return cls._jwks_client

    async def dispatch(self, request: Request, call_next):
        # Skip auth for health checks
        if request.url.path == "/healthz":
            return await call_next(request)

        # Skip auth in dev mode or when Keycloak is not configured
        if not settings.auth.keycloak_enabled:
            return await call_next(request)

        # Require bearer token
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Missing bearer token"},
                status_code=401,
            )

        token = auth_header[7:]

        try:
            payload = await self._validate_jwt(token)
        except _AuthError as e:
            return JSONResponse({"error": str(e)}, status_code=401)
        except Exception:
            return JSONResponse(
                {"error": "Auth service unavailable"},
                status_code=503,
            )

        # Stash the provider_id (Keycloak `sub`) on request state.
        # Tools can read this via ctx.request_context.request.state.auth_provider_id
        # The mapping value MUST be the Keycloak user's `sub`, not a username.
        azp = payload.get("azp", "")
        request.state.auth_provider_id = settings.auth.client_user_mapping.get(azp, "")

        return await call_next(request)

    async def _validate_jwt(self, token: str) -> dict:
        """Verify JWT signature and claims using Keycloak JWKS.

        Returns the decoded JWT payload on success.
        """
        # PyJWKClient fetches JWKS, caches it, and selects the right key by kid
        signing_key = self._get_jwks_client().get_signing_key_from_jwt(token)

        try:
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=settings.auth.keycloak_issuer,
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError:
            raise _AuthError("Token expired")
        except jwt.InvalidIssuerError:
            raise _AuthError("Token from wrong issuer")
        except jwt.InvalidTokenError as e:
            raise _AuthError(f"Invalid token: {e}")

        # Verify the authorized party (client ID) if configured
        expected_client = settings.auth.keycloak_client_id
        if expected_client and payload.get("azp") != expected_client:
            raise _AuthError("Token from unauthorized client")

        return payload


app.add_middleware(BearerAuthMiddleware)


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
