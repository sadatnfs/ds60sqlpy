"""Loopback-only ASGI workshop with authenticated, explicit SSE readback."""

from __future__ import annotations

import asyncio
import hmac
import os
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from serving_contract import MAX_BODY, ContractError, RequestSpec, exact_json, sse_frame
from serving_engine import InferenceEngine
from serving_scheduler import Busy, Scheduler
from serving_store import RecordStore, StoreFull, record_bytes
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from starlette.routing import Route

ROOT = Path(__file__).resolve().parent


def public_origin(value: str) -> str:
    parsed = urlsplit(value)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Public origin has an invalid port") from exc
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or port is None
        or not 1024 <= port <= 65535
        or parsed.path
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Set the exact loopback origin, for example http://127.0.0.1:8892")
    return value


class LocalBoundary:
    def __init__(self, app: Any, *, origin: str, token: str) -> None:
        self.app = app
        self.origin = origin
        self.host = urlsplit(origin).netloc.encode()
        self.token = token

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = scope["headers"]

        def values(name: bytes) -> list[bytes]:
            return [value for key, value in headers if key.lower() == name]

        hosts = values(b"host")
        origins = values(b"origin")
        sites = values(b"sec-fetch-site")
        method = scope["method"]
        path = scope["path"]
        valid = (
            hosts == [self.host]
            and len(origins) <= 1
            and (not origins or origins == [self.origin.encode()])
        )
        valid = valid and len(sites) <= 1 and (not sites or sites[0] in {b"same-origin", b"none"})
        if method not in {"GET", "HEAD", "POST"}:
            valid = False
        if method == "POST" and origins != [self.origin.encode()]:
            valid = False
        if path.startswith("/api/"):
            supplied = values(b"x-workshop-token")
            valid = (
                valid
                and len(supplied) == 1
                and hmac.compare_digest(supplied[0], self.token.encode())
            )
        if not valid:
            await JSONResponse(
                {"error": "Local Host, origin or authentication check failed"}, status_code=403
            )(scope, receive, send)
            return

        async def secure_send(message: Any) -> None:
            if message["type"] == "http.response.start":
                additions = [
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"x-frame-options", b"DENY"),
                    (
                        b"content-security-policy",
                        (
                            b"default-src 'none'; script-src 'self'; style-src 'self'; "
                            b"connect-src 'self'; img-src 'self'; base-uri 'none'; "
                            b"form-action 'none'; frame-ancestors 'none'"
                        ),
                    ),
                ]
                message["headers"] = [*message.get("headers", []), *additions]
            await send(message)

        await self.app(scope, receive, secure_send)


def create_app() -> Any:
    origin = public_origin(os.environ.get("DS60_PUBLIC_ORIGIN", "http://127.0.0.1:8892"))
    token_path = Path(os.environ["DS60_TOKEN_FILE"])
    if token_path.is_symlink() or not token_path.is_file() or token_path.stat().st_size != 65:
        raise ValueError("Prepare the dedicated 64-character workshop token file")
    token = token_path.read_text().strip()
    if re.fullmatch(r"[0-9a-f]{64}", token) is None:
        raise ValueError("Malformed workshop token")
    model_path = Path(os.environ["DS60_MODEL_DIR"])
    state_path = Path(os.environ["DS60_STATE_DIR"])
    engine: InferenceEngine | None = None
    scheduler: Scheduler | None = None

    @asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        nonlocal engine, scheduler
        engine = await asyncio.to_thread(
            InferenceEngine,
            model_path,
            os.environ.get("DS60_DEVICE", "cpu"),
            float(os.environ.get("DS60_PACING_SECONDS", "0")),
        )
        store = RecordStore(state_path)
        try:
            scheduler = Scheduler(engine, store)
        except BaseException:
            store.close()
            raise
        scheduler.start()
        app.state.engine = engine
        app.state.scheduler = scheduler
        try:
            yield
        finally:
            await scheduler.close()

    def active() -> tuple[InferenceEngine, Scheduler]:
        if engine is None or scheduler is None:
            raise RuntimeError("Startup has not completed")
        return engine, scheduler

    async def home(request: Request) -> Response:
        html = (ROOT / "index.html").read_text().replace("WORKSHOP_TOKEN_PLACEHOLDER", token)
        return HTMLResponse(html)

    async def static(request: Request) -> Response:
        name = request.path_params["name"]
        if name not in {"app.js", "style.css"}:
            return JSONResponse({"error": "Unknown asset"}, status_code=404)
        return Response(
            (ROOT / name).read_bytes(),
            media_type="text/javascript" if name.endswith(".js") else "text/css",
        )

    async def health(request: Request) -> Response:
        return JSONResponse({"ready": engine is not None and scheduler is not None})

    async def status(request: Request) -> Response:
        model, manager = active()
        return JSONResponse(
            {
                **model.describe(),
                "running": manager.running,
                "waiting": len(manager.pending),
                "reserved_tokens": manager.reserved_tokens,
                "history_count": len(manager.records),
                "history_limit": 128,
                "scheduler": "one compute slot, FIFO, two waiting reservations",
            }
        )

    async def create(request: Request) -> Response:
        _, manager = active()
        content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json" or request.query_params:
            return JSONResponse(
                {"error": "Use application/json without query parameters"}, status_code=415
            )
        chunks = bytearray()
        try:
            async with asyncio.timeout(5):
                async for chunk in request.stream():
                    chunks.extend(chunk)
                    if len(chunks) > MAX_BODY:
                        return JSONResponse(
                            {"error": "Request body exceeds 8000 bytes"}, status_code=413
                        )
        except TimeoutError:
            return JSONResponse(
                {"error": "Request body did not arrive within five seconds"}, status_code=408
            )
        try:
            spec = RequestSpec.parse(exact_json(bytes(chunks)))
            result, created = await manager.submit(spec)
            return JSONResponse({**result, "created": created}, status_code=202 if created else 200)
        except ContractError as exc:
            return JSONResponse(
                {"error": str(exc)}, status_code=409 if "already belongs" in str(exc) else 400
            )
        except (Busy, StoreFull) as exc:
            return JSONResponse({"error": str(exc)}, status_code=429, headers={"Retry-After": "2"})
        except OSError:
            return JSONResponse(
                {"error": "Request could not be saved; no inference was admitted"}, status_code=507
            )

    async def history(request: Request) -> Response:
        _, manager = active()
        return JSONResponse(
            {"requests": [manager.state(identity) for identity in reversed(manager.records)]}
        )

    async def receipt(request: Request) -> Response:
        _, manager = active()
        identity = request.path_params["identity"]
        if identity not in manager.records:
            return JSONResponse({"error": "Unknown request ID"}, status_code=404)
        raw = record_bytes(manager.records[identity])
        return Response(
            raw,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="inference-{identity}.json"'},
        )

    async def cancel(request: Request) -> Response:
        _, manager = active()
        try:
            return JSONResponse(await manager.cancel(request.path_params["identity"]))
        except KeyError:
            return JSONResponse({"error": "Unknown request ID"}, status_code=404)

    async def events(request: Request) -> Response:
        _, manager = active()
        identity = request.path_params["identity"]
        query = list(request.query_params.multi_items())
        cursors = request.headers.getlist("last-event-id")
        if (
            len(cursors) > 1
            or (query and cursors)
            or any(key != "after" for key, _ in query)
            or len(query) > 1
        ):
            return JSONResponse({"error": "Supply one explicit event cursor"}, status_code=400)
        raw = cursors[0] if cursors else query[0][1] if query else "0"
        if re.fullmatch(r"0|[1-9][0-9]{0,2}", raw) is None:
            return JSONResponse({"error": "Invalid event cursor"}, status_code=400)
        try:
            iterator = await manager.subscribe(identity, int(raw))
        except KeyError:
            return JSONResponse({"error": "Unknown request ID"}, status_code=404)
        except ContractError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
        except Busy as exc:
            return JSONResponse({"error": str(exc)}, status_code=409)

        async def stream() -> AsyncIterator[bytes]:
            try:
                async for item in iterator:
                    yield sse_frame(item)
            finally:
                await iterator.aclose()  # type: ignore[attr-defined]

        return StreamingResponse(
            stream(), media_type="text/event-stream", headers={"X-Accel-Buffering": "no"}
        )

    application = Starlette(
        lifespan=lifespan,
        routes=[
            Route("/", home),
            Route("/assets/{name}", static),
            Route("/healthz", health),
            Route("/api/status", status),
            Route("/api/requests", create, methods=["POST"]),
            Route("/api/requests", history),
            Route("/api/requests/{identity}", receipt),
            Route("/api/requests/{identity}/cancel", cancel, methods=["POST"]),
            Route("/api/requests/{identity}/events", events),
        ],
    )
    return LocalBoundary(application, origin=origin, token=token)
