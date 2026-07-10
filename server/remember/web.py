"""Web UI server for REMEMBER.

Browser-based OAuth flow via Keycloak (authorization_code grant):
  1. User visits / → static UI shell loads (no sensitive data)
  2. JS calls /api/* → 401 if not authenticated → JS redirects to /login
  3. /login → redirect to Keycloak authorization endpoint
  4. User logs in at Keycloak → redirected back to /auth/callback
  5. /auth/callback → exchange code for tokens → store in session cookie → redirect /
  6. JS retries /api/* with session cookie → succeeds

Session cookies are signed + encrypted by SessionMiddleware using session_secret.
Access tokens are stored in the session and used for DB operations.
"""

import json
import os
import secrets
import uuid
from pathlib import Path
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

from remember.config import settings
from remember.db import async_session_factory
from remember.models import User
from remember.tools import (
    search_memories,
    save_memory,
    get_memory,
    list_memories,
    verify_memory,
    archive_memory,
    refute_memory,
)

app = FastAPI(title="REMEMBER Web UI")


# ---------------------------------------------------------------------------
# No-cache middleware — ensure browsers always revalidate static assets.
# StaticFiles sends ETags, so no-cache means a cheap 304 when unchanged
# and fresh content when updated. Prevents stale app.js after deploys.
# ---------------------------------------------------------------------------


class NoCacheMiddleware(BaseHTTPMiddleware):
    """Set Cache-Control: no-cache on all responses so browsers revalidate."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
        return response


# Session middleware — signs/encrypts the session cookie
# In dev mode, use a fixed dummy secret; in production, require a real secret
_session_secret = settings.auth.session_secret or "dev-only-insecure-secret-change-me"
app.add_middleware(SessionMiddleware, secret_key=_session_secret, https_only=True, same_site="lax")
app.add_middleware(NoCacheMiddleware)

# Static files — mounted at root AFTER all routes (see bottom of file)
webui_path = Path(__file__).parent.parent / "webui"


# ---------------------------------------------------------------------------
# OAuth configuration (from settings)
# ---------------------------------------------------------------------------

def _keycloak_enabled() -> bool:
    return bool(settings.auth.keycloak_authority) and not settings.auth.dev_mode


def _keycloak_base() -> str:
    return f"{settings.auth.keycloak_authority}/realms/{settings.auth.keycloak_realm}"


def _redirect_uri() -> str:
    # Construct from the request — but in production behind traefik, use a fixed URL
    return os.getenv("REMEMBER_OAUTH_REDIRECT_URI", "https://remember.cdd.net.au/auth/callback")


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.get("/login")
async def login(request: Request):
    """Redirect to Keycloak authorization endpoint.

    Includes a random state parameter to prevent login CSRF.
    The state is stored in the session and verified in the callback.
    """
    if not _keycloak_enabled():
        return RedirectResponse("/")

    # Generate a random state parameter to prevent login CSRF
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    params = {
        "client_id": settings.auth.keycloak_client_id,
        "redirect_uri": _redirect_uri(),
        "response_type": "code",
        "scope": "openid profile email",
        "state": state,
    }
    auth_url = f"{_keycloak_base()}/protocol/openid-connect/auth?{urlencode(params)}"
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
async def auth_callback(
    code: str,
    state: str,
    request: Request,
):
    """Exchange authorization code for tokens, store in session, redirect home.

    Security:
    - Verifies the state parameter matches the one stored in the session
      to prevent login CSRF.
    - Fails hard (403) if Keycloak userinfo is unavailable — no silent
      fallback to a default user.
    """
    if not _keycloak_enabled():
        return RedirectResponse("/")

    # Verify state parameter to prevent login CSRF
    expected_state = request.session.pop("oauth_state", None)
    if not expected_state or not secrets.compare_digest(state, expected_state):
        raise HTTPException(status_code=403, detail="Invalid OAuth state — possible login CSRF attempt")

    # Exchange code for tokens
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{_keycloak_base()}/protocol/openid-connect/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.auth.keycloak_client_id,
                "client_secret": settings.auth.keycloak_client_secret,
                "code": code,
                "redirect_uri": _redirect_uri(),
            },
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    tokens = resp.json()

    # Get user info from the access token
    async with httpx.AsyncClient(timeout=10.0) as client:
        userinfo_resp = await client.get(
            f"{_keycloak_base()}/protocol/openid-connect/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

    if userinfo_resp.status_code != 200:
        # C3 fix: fail hard, do NOT fall back to a default UUID
        raise HTTPException(status_code=502, detail="Keycloak userinfo endpoint unavailable")

    user_info = userinfo_resp.json()

    if not user_info or "sub" not in user_info:
        # C3 fix: fail hard, do NOT fall back to a default UUID
        raise HTTPException(status_code=502, detail="Keycloak returned incomplete user info")

    # Get or create user in database
    user_id = await _get_or_create_user(user_info)

    # Store tokens + user_id in the session
    request.session["access_token"] = tokens["access_token"]
    request.session["refresh_token"] = tokens.get("refresh_token", "")
    request.session["user_id"] = str(user_id)

    return RedirectResponse("/")


@app.get("/logout")
async def logout(request: Request):
    """Clear session and redirect to Keycloak logout."""
    request.session.clear()

    if _keycloak_enabled():
        params = {
            "client_id": settings.auth.keycloak_client_id,
            "post_logout_redirect_uri": "https://remember.cdd.net.au/",
        }
        logout_url = f"{_keycloak_base()}/protocol/openid-connect/logout?{urlencode(params)}"
        return RedirectResponse(logout_url)

    return RedirectResponse("/")


@app.get("/auth/status")
async def auth_status(request: Request):
    """Check if the current session is authenticated. Used by the JS UI."""
    user_id = request.session.get("user_id")
    if user_id:
        return {"authenticated": True, "user_id": user_id}
    return {"authenticated": False}


# ---------------------------------------------------------------------------
# Session-based auth dependency
# ---------------------------------------------------------------------------

async def get_current_user(request: Request) -> uuid.UUID:
    """Extract user ID from the session cookie. Redirects to /login if missing."""
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Check if access token is still present (session may have expired)
    access_token = request.session.get("access_token")
    if not access_token:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Session expired")

    return uuid.UUID(user_id_str)


# ---------------------------------------------------------------------------
# Helper: get or create user from Keycloak userinfo
# ---------------------------------------------------------------------------

async def _get_or_create_user(user_info: dict) -> uuid.UUID:
    """Get or create a user record from Keycloak userinfo.

    Raises ValueError if userinfo is incomplete — caller must handle
    (the /auth/callback endpoint returns 502 in this case).
    """
    if not user_info or "sub" not in user_info:
        raise ValueError("Incomplete Keycloak userinfo: missing 'sub' claim")

    provider_id = str(user_info["sub"])

    async with async_session_factory() as db:
        from sqlalchemy import select

        stmt = select(User).where(
            User.provider == "keycloak",
            User.provider_id == provider_id,
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            return user.id

        user = User(
            id=uuid.uuid4(),
            provider="keycloak",
            provider_id=provider_id,
            display_name=user_info.get("preferred_username", user_info.get("name", "Unknown")),
            email=user_info.get("email"),
        )
        db.add(user)
        await db.commit()
        return user.id


# ---------------------------------------------------------------------------
# API endpoints (all protected by get_current_user)
# ---------------------------------------------------------------------------

@app.get("/healthz")
async def healthz():
    """Health check endpoint — no auth required."""
    return {"status": "healthy", "service": "remember-webui"}


@app.get("/api/search")
async def api_search(
    query: str,
    user_id: uuid.UUID = Depends(get_current_user),
    type: str | None = None,
    status: str | None = None,
    limit: int = 50,
):
    """Search memories via HTTP API."""
    async with async_session_factory() as db:
        results = await search_memories(
            query=query,
            types=[type] if type else None,
            limit=limit,
            owner_id=user_id,
            db=db,
        )
    return results


@app.get("/api/get/{memory_id}")
async def api_get(
    memory_id: str,
    user_id: uuid.UUID = Depends(get_current_user),
):
    """Get memory details via HTTP API."""
    async with async_session_factory() as db:
        result = await get_memory(
            memory_id=uuid.UUID(memory_id),
            user_id=user_id,
            db=db,
        )
    if not result:
        raise HTTPException(status_code=404, detail="Memory not found")
    return result


@app.post("/api/save")
async def api_save(
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user),
):
    """Save memory via HTTP API."""
    data = await request.json()
    required = ["name", "type", "description", "body"]
    missing = [f for f in required if f not in data]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing fields: {missing}")

    async with async_session_factory() as db:
        result = await save_memory(
            name=data["name"],
            type=data["type"],
            description=data["description"],
            body=data["body"],
            owner_id=user_id,
            tags=data.get("tags"),
            db=db,
        )
    return result


@app.post("/api/verify/{memory_id}")
async def api_verify(
    memory_id: str,
    user_id: uuid.UUID = Depends(get_current_user),
):
    """Verify memory via HTTP API."""
    async with async_session_factory() as db:
        result = await verify_memory(
            memory_id=uuid.UUID(memory_id),
            user_id=user_id,
            db=db,
        )
    return result


@app.post("/api/archive/{memory_id}")
async def api_archive(
    memory_id: str,
    user_id: uuid.UUID = Depends(get_current_user),
):
    """Archive memory via HTTP API."""
    async with async_session_factory() as db:
        result = await archive_memory(
            memory_id=uuid.UUID(memory_id),
            user_id=user_id,
            db=db,
        )
    return result


@app.post("/api/refute/{memory_id}")
async def api_refute(
    memory_id: str,
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user),
):
    """Refute memory via HTTP API."""
    data = await request.json()
    async with async_session_factory() as db:
        result = await refute_memory(
            memory_id=uuid.UUID(memory_id),
            user_id=user_id,
            reason=data.get("reason", "Refuted via web UI"),
            db=db,
        )
    return result


# Serve static files at root (catch-all, AFTER all API/auth routes).
# html=True means / serves index.html; relative paths (styles.css, app.js)
# resolve correctly at the root level.
app.mount("/", StaticFiles(directory=str(webui_path), html=True), name="static")


def run_webui(host: str = "0.0.0.0", port: int = 3000):
    """Run the web UI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_webui()