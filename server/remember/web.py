"""Web UI server for REMEMBER."""

import json
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from remember.db import async_session_factory
from remember.models import Memory
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

# Serve static files
webui_path = Path(__file__).parent.parent.parent / "webui"
app.mount("/static", StaticFiles(directory=str(webui_path)), name="static")

templates = Jinja2Templates(directory=str(webui_path))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the web UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"status": "healthy", "service": "remember-webui"}


@app.get("/api/search")
async def api_search(
    q: str,
    type: str | None = None,
    status: str | None = None,
    limit: int = 50,
):
    """Search memories via HTTP API."""
    async with async_session_factory() as db:
        results = await search_memories(
            query=q,
            types=[type] if type else None,
            limit=limit,
            db=db,
        )
    return results


@app.get("/api/get/{memory_id}")
async def api_get(memory_id: str, user_id: str = "webui-user"):
    """Get memory details via HTTP API."""
    import uuid
    user_uuid = uuid.UUID(user_id) if user_id != "webui-user" else None
    async with async_session_factory() as db:
        result = await get_memory(
            memory_id=uuid.UUID(memory_id),
            user_id=user_uuid,
            db=db,
        )
    if not result:
        raise HTTPException(status_code=404, detail="Memory not found")
    return result


@app.post("/api/save")
async def api_save(request: Request):
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
            owner_id=__default_owner_id__,
            tags=data.get("tags"),
            db=db,
        )
    return result


@app.post("/api/verify/{memory_id}")
async def api_verify(memory_id: str):
    """Verify memory via HTTP API."""
    async with async_session_factory() as db:
        result = await verify_memory(
            memory_id=uuid.UUID(memory_id),
            user_id=__default_owner_id__,
            db=db,
        )
    return result


@app.post("/api/archive/{memory_id}")
async def api_archive(memory_id: str):
    """Archive memory via HTTP API."""
    async with async_session_factory() as db:
        result = await archive_memory(
            memory_id=uuid.UUID(memory_id),
            user_id=__default_owner_id__,
            db=db,
        )
    return result


@app.post("/api/refute/{memory_id}")
async def api_refute(memory_id: str, request: Request):
    """Refute memory via HTTP API."""
    data = await request.json()
    async with async_session_factory() as db:
        result = await refute_memory(
            memory_id=uuid.UUID(memory_id),
            user_id=__default_owner_id__,
            reason=data.get("reason", "Refuted via web UI"),
            db=db,
        )
    return result


# Default owner for web UI (in production, use auth)
import uuid as _uuid
__default_owner_id__ = _uuid.UUID("00000000-0000-0000-0000-000000000001")


def run_webui(host: str = "0.0.0.0", port: int = 3000):
    """Run the web UI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_webui()
