"""FastAPI HTTP, finite WebSocket and controlled durable SSE workshop."""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Annotated

import store
from fastapi import Depends, FastAPI, Header, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from request_limits import BodyLimit

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="Python web workshop", version="1.0", docs_url=None, redoc_url=None)
app.add_middleware(BodyLimit, limit=16384)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
app.mount("/static", StaticFiles(directory=STATIC), name="static")
COOKIE = "pyweb_fastapi"


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    username: str = Field(max_length=128)
    password: str = Field(max_length=128)


class NoteInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str = Field(min_length=1, max_length=120)


class JobInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    values: list[int] = Field(min_length=1, max_length=32)


@app.exception_handler(store.Rejected)
async def rejected(request: Request, error: store.Rejected):
    return JSONResponse({"error": str(error)}, status_code=error.status)


@app.middleware("http")
async def response_headers(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and (not length.isdecimal() or int(length) > 16384):
        return JSONResponse({"error": "Request body too large"}, status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    )
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


def principal(request: Request):
    return store.identity("fastapi", request.cookies.get(COOKIE))


def writer(request: Request):
    return store.write_identity(
        "fastapi",
        request.cookies.get(COOKIE),
        request.headers.get("X-CSRF-Token"),
        request.headers.get("Origin"),
    )


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/docs", include_in_schema=False)
def docs():
    return FileResponse(STATIC / "docs.html")


@app.get("/config", include_in_schema=False)
def config():
    return {"framework": "FastAPI", "jobs": True, "origin": os.environ["WEB_ORIGIN"]}


@app.get("/healthz")
def health():
    with store.connect() as conn:
        conn.execute("SELECT 1").fetchone()
    return {"status": "ready", "framework": "FastAPI"}


@app.post("/api/login")
def login(payload: Credentials, request: Request):
    store.require_origin(request.headers.get("Origin"))
    token, body = store.login("fastapi", payload.model_dump())
    response = JSONResponse(body)
    response.set_cookie(COOKIE, token, httponly=True, samesite="lax", max_age=7200)
    return response


@app.get("/api/me")
def me(user: Annotated[dict, Depends(principal)]):
    return {"username": user["username"], "csrf": user["csrf"]}


@app.post("/api/logout")
def logout(request: Request, user: Annotated[dict, Depends(writer)]):
    store.logout(request.cookies[COOKIE])
    response = JSONResponse({"logged_out": True})
    response.delete_cookie(COOKIE)
    return response


@app.get("/api/notes")
def notes(user: Annotated[dict, Depends(principal)]):
    return {"notes": store.notes("fastapi", user["id"])}


@app.post("/api/notes", status_code=201)
def create_note(payload: NoteInput, user: Annotated[dict, Depends(writer)]):
    return store.notes("fastapi", user["id"], payload.model_dump())


@app.get("/api/notes/{identifier}")
def detail(identifier: int, user: Annotated[dict, Depends(principal)]):
    return store.read_note("fastapi", user["id"], identifier)


@app.post("/api/jobs", status_code=202)
def create_job(payload: JobInput, user: Annotated[dict, Depends(writer)]):
    return store.create_job(user["id"], payload.model_dump())


@app.get("/api/jobs/{identifier}")
def job(identifier: str, user: Annotated[dict, Depends(principal)]):
    return store.job(user["id"], identifier)


@app.post("/api/jobs/{identifier}/release")
def release(identifier: str, user: Annotated[dict, Depends(writer)]):
    return store.release(user["id"], identifier)


@app.get("/api/jobs/{identifier}/events")
async def stream(
    identifier: str,
    request: Request,
    user: Annotated[dict, Depends(principal)],
    last_event_id: Annotated[str | None, Header()] = None,
):
    if last_event_id and (
        not last_event_id.isascii() or not last_event_id.isdecimal() or len(last_event_id) > 18
    ):
        raise store.Rejected(400, "Invalid event cursor")
    after = int(last_event_id or 0)
    await asyncio.to_thread(store.events, user["id"], identifier, after)

    async def frames():
        cursor, deadline = after, time.monotonic() + 30
        while time.monotonic() < deadline:
            if await request.is_disconnected():
                return
            rows = await asyncio.to_thread(store.events, user["id"], identifier, cursor)
            for row in rows:
                cursor = row["id"]
                yield f"id: {cursor}\nevent: progress\ndata: {json.dumps(row)}\n\n"
                if row["state"] == "finished":
                    return
            yield ": heartbeat\n\n"
            await asyncio.sleep(0.2)

    return StreamingResponse(
        frames(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.websocket("/socket")
async def socket(websocket: WebSocket):
    try:
        store.require_origin(websocket.headers.get("origin"))
        user = await asyncio.to_thread(store.identity, "fastapi", websocket.cookies.get(COOKIE))
    except store.Rejected:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        async with asyncio.timeout(10):
            text = await websocket.receive_text()
        if len(text.encode()) > 256:
            await websocket.close(code=1009)
            return
        try:
            payload = json.loads(text)
        except ValueError:
            await websocket.close(code=1008)
            return
        if (
            not isinstance(payload, dict)
            or set(payload) != {"message"}
            or not isinstance(payload["message"], str)
            or not 1 <= len(payload["message"]) <= 80
        ):
            await websocket.close(code=1008)
            return
        await websocket.send_json({"user": user["username"], "echo": payload["message"]})
        await websocket.close(code=1000)
    except (WebSocketDisconnect, TimeoutError):
        return
