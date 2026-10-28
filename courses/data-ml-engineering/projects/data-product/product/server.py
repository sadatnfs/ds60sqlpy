"""Bounded local HTTP raw acceptance, separate from analytical publication."""

from __future__ import annotations

import hmac
import io
import json
import os
import re
import socket
import sqlite3
import threading
import time
from collections.abc import Callable, Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer
from typing import Any
from urllib.parse import urlsplit

from .contracts import (
    HEX,
    MAX_BODY,
    ConflictError,
    ContractError,
    StateError,
    identifier,
    owner_identity,
    read_regular,
    strict_json,
    validate_snapshot,
)
from .raw_store import RawStore

IO_TIMEOUT = 5.0
MAX_HANDLERS = 4
MAX_RESPONSE = 65_536
ProductReader = Callable[[Path, str], dict[str, Any]]
ServerRequest = socket.socket | tuple[bytes, socket.socket]


def read_published(directory: Path, owner: str) -> dict[str, Any]:
    # Publication is a separately owned component. Collection/import of this
    # server and its raw-store tests does not require that component to exist.
    from .publication import read_product

    return read_product(directory, owner)


def public_identity(origin: str) -> tuple[str, str]:
    try:
        parts = urlsplit(origin)
        port = parts.port
    except ValueError as error:
        raise StateError("Use one exact loopback HTTP public origin") from error
    if (
        parts.scheme != "http"
        or parts.hostname != "127.0.0.1"
        or port is None
        or not 1 <= port <= 65535
        or origin != f"http://127.0.0.1:{port}"
    ):
        raise StateError("Use one exact loopback HTTP public origin")
    return origin, f"127.0.0.1:{port}"


class DeadlineReader(io.RawIOBase):
    """An absolute request deadline also bounds slow headers and partial bodies."""

    def __init__(self, connection: socket.socket, deadline: float) -> None:
        super().__init__()
        self.connection, self.deadline = connection, deadline

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: Any) -> int:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Request read deadline exceeded")
        self.connection.settimeout(remaining)
        return self.connection.recv_into(buffer)


class ProductHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False
    request_queue_size = 8
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        *,
        raw_store: RawStore,
        owner: str,
        token: str,
        published_directory: Path,
        public_origin: str | None = None,
        product_reader: ProductReader | None = None,
        io_timeout: float = IO_TIMEOUT,
    ) -> None:
        self.owner = owner_identity(owner)
        if raw_store.owner != self.owner:
            raise StateError("HTTP and raw-store ownership differ")
        if HEX.fullmatch(token) is None:
            raise StateError("Use one private 64-character lowercase ASCII hex token")
        if published_directory.is_symlink() or not published_directory.is_dir():
            raise StateError("Use the owned existing publication directory")
        if not 0 < io_timeout <= IO_TIMEOUT:
            raise StateError("Request deadlines must be positive and at most five seconds")
        self.raw_store, self.token = raw_store, token
        self.published_directory = published_directory
        self.product_reader = product_reader or read_published
        self.io_timeout = io_timeout
        self.handlers = threading.BoundedSemaphore(MAX_HANDLERS)
        if public_origin is not None:
            public_identity(public_origin)
        super().__init__(address, ProductHandler)
        try:
            origin = public_origin or f"http://127.0.0.1:{self.server_port}"
            self.public_origin, self.public_host = public_identity(origin)
        except BaseException:
            self.server_close()
            raise

    def server_bind(self) -> None:
        # HTTPServer's reverse-DNS name lookup is unnecessary for a fixed local
        # fixture and must not make offline startup depend on name resolution.
        TCPServer.server_bind(self)
        self.server_name = str(self.server_address[0])
        self.server_port = int(self.server_address[1])

    def process_request(self, request: ServerRequest, client_address: Any) -> None:
        if not isinstance(request, socket.socket):
            raise TypeError("The data-product server accepts TCP sockets only")
        request.settimeout(self.io_timeout)
        if not self.handlers.acquire(blocking=False):
            body = b'{"error":"Service busy"}'
            response = (
                b"HTTP/1.0 503 Service Unavailable\r\n"
                b"Content-Type: application/json\r\nConnection: close\r\n"
                + f"Content-Length: {len(body)}\r\n\r\n".encode()
                + body
            )
            try:
                request.sendall(response)
            except OSError:
                pass
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.handlers.release()
            raise

    def process_request_thread(self, request: ServerRequest, client_address: Any) -> None:
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.handlers.release()

    def handle_error(self, request: ServerRequest, client_address: Any) -> None:
        # No header/body/URL traceback logging. Requests have controlled responses;
        # disconnects do not authorize repeating a committed raw acceptance.
        return


class ProductHandler(BaseHTTPRequestHandler):
    server: ProductHTTPServer
    raw_requestline: bytes
    protocol_version = "HTTP/1.0"
    server_version = "DS60Product"
    sys_version = ""

    def setup(self) -> None:
        super().setup()
        self.rfile.close()
        self.rfile = io.BufferedReader(
            DeadlineReader(self.connection, time.monotonic() + self.server.io_timeout),
            buffer_size=8192,
        )

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        self.request_version = "HTTP/1.0"
        self.respond(400, {"error": "Malformed or unsupported HTTP request"})

    def respond(self, code: int, value: Any) -> None:
        self.close_connection = True
        try:
            body = json.dumps(
                value, sort_keys=True, separators=(",", ":"), allow_nan=False
            ).encode()
            if len(body) > MAX_RESPONSE:
                code, body = 503, b'{"error":"Response exceeds its declared bound"}'
        except (TypeError, ValueError, RecursionError):
            code, body = 503, b'{"error":"Verified response unavailable"}'
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if getattr(self, "command", "") != "HEAD":
                self.wfile.write(body)
        except OSError:
            # A disconnected client must reconcile by batch ID. Never accept
            # again or change the committed outcome to manufacture a response.
            return

    def parse_request(self) -> bool:
        self.requestline = ""
        self.command = ""
        self.close_connection = True
        pieces = self.raw_requestline.rstrip(b"\r\n").split()
        if len(pieces) != 3:
            self.request_version = "HTTP/1.0"
            self.respond(400, {"error": "Use a complete origin-form HTTP request"})
            return False
        try:
            original_path = pieces[1].decode("ascii")
        except UnicodeError:
            self.request_version = "HTTP/1.0"
            self.respond(400, {"error": "Use an ASCII origin-form path"})
            return False
        try:
            if not super().parse_request():
                return False
        except (OSError, ValueError):
            self.respond(400, {"error": "Request header deadline or syntax failure"})
            return False
        if original_path != self.path:
            self.respond(400, {"error": "Ambiguous path is unsupported"})
            return False
        return True

    def request_boundary(self, *, write: bool = False) -> bool:
        path = self.path
        if (
            not path.startswith("/")
            or any(character in path for character in ["%", "?", "#", "\\", ";"])
            or "//" in path
            or any(part in {".", ".."} for part in path.split("/"))
            or any(ord(character) < 33 or ord(character) > 126 for character in path)
        ):
            self.respond(400, {"error": "Ambiguous path is unsupported"})
            return False
        hosts = self.headers.get_all("Host", [])
        if hosts != [self.server.public_host]:
            self.respond(403, {"error": "Host is not the saved public host"})
            return False
        origins = self.headers.get_all("Origin", [])
        if (write and origins != [self.server.public_origin]) or (
            origins and origins != [self.server.public_origin]
        ):
            self.respond(403, {"error": "Origin is not the saved public origin"})
            return False
        if self.headers.get_all("Transfer-Encoding") or self.headers.get_all("Expect"):
            self.respond(400, {"error": "Transfer encoding and expectations are unsupported"})
            return False
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) > 1 or (not write and lengths not in [[], ["0"]]):
            self.respond(400, {"error": "Ambiguous or unexpected content length"})
            return False
        if not write and path == "/healthz":
            return True
        tokens = self.headers.get_all("X-DS60-Product-Token", [])
        if (
            len(tokens) != 1
            or HEX.fullmatch(tokens[0]) is None
            or not hmac.compare_digest(tokens[0], self.server.token)
        ):
            self.respond(403, {"error": "Private product token required"})
            return False
        return True

    def publication_status(self) -> tuple[dict[str, Any], dict[str, Any] | None]:
        try:
            product = self.server.product_reader(self.server.published_directory, self.server.owner)
            if type(product) is not dict or set(product) != {"pointer", "manifest", "rows"}:
                raise StateError("Verified product response has an incompatible shape")
            return {"status": "available", "pointer": product["pointer"]}, product
        except FileNotFoundError:
            return {"status": "absent"}, None
        except Exception:
            return {"status": "corrupt"}, None

    def do_GET(self) -> None:
        if not self.request_boundary():
            return
        try:
            if self.path == "/healthz":
                self.server.raw_store.receipts()
                self.respond(200, {"status": "ok", "raw_ready": True})
            elif self.path == "/api/status":
                receipts = self.server.raw_store.receipts()
                publication, _ = self.publication_status()
                self.respond(
                    200,
                    {"raw_ready": True, "raw_snapshots": len(receipts), "publication": publication},
                )
            elif self.path == "/api/snapshots":
                self.respond(200, {"snapshots": self.server.raw_store.receipts()})
            elif self.path.startswith("/api/snapshots/"):
                batch = self.path.removeprefix("/api/snapshots/")
                identifier(batch, "Batch identity")
                self.respond(200, self.server.raw_store.get(batch))
            elif self.path == "/api/product":
                status, product = self.publication_status()
                if status["status"] == "absent":
                    self.respond(404, {"error": "No analytical product has been published"})
                elif product is None:
                    self.respond(503, {"error": "Analytical product failed verification"})
                else:
                    self.respond(200, product)
            else:
                self.respond(404, {"error": "Unknown fixed route"})
        except KeyError:
            self.respond(404, {"error": "Unknown raw snapshot"})
        except ContractError:
            self.respond(400, {"error": "Invalid snapshot identity"})
        except (StateError, OSError, sqlite3.Error):
            self.respond(503, {"error": "Raw state unavailable", "raw_ready": False})
        except Exception:
            self.respond(503, {"error": "Request could not be completed"})

    def do_POST(self) -> None:
        if not self.request_boundary(write=True):
            return
        if self.path != "/api/snapshots":
            self.respond(404, {"error": "Unknown fixed write route"})
            return
        lengths = self.headers.get_all("Content-Length", [])
        content_types = self.headers.get_all("Content-Type", [])
        if (
            len(lengths) != 1
            or re.fullmatch(r"[1-9][0-9]{0,5}", lengths[0], flags=re.ASCII) is None
            or int(lengths[0]) > MAX_BODY
            or len(content_types) != 1
            or re.fullmatch(
                r"application/json(?:;[ \t]*charset=utf-8)?",
                content_types[0],
                flags=re.I | re.ASCII,
            )
            is None
        ):
            self.respond(400, {"error": "Use one bounded JSON body and exact content length"})
            return
        try:
            length = int(lengths[0])
            body = self.rfile.read(length)
            if len(body) != length:
                raise ContractError("Incomplete request body")
            value = validate_snapshot(strict_json(body))
            receipt, created = self.server.raw_store.accept(value)
            self.respond(201 if created else 200, {"receipt": receipt, "created": created})
        except (ContractError, TimeoutError):
            self.respond(
                400, {"error": "Request body deadline or complete snapshot contract failed"}
            )
        except ConflictError:
            self.respond(409, {"error": "Raw snapshot identity or generation conflicts"})
        except (StateError, OSError, sqlite3.Error):
            self.respond(503, {"error": "Raw acceptance unavailable; reconcile the batch identity"})
        except Exception:
            self.respond(503, {"error": "Raw acceptance outcome requires reconciliation"})


def create_server(
    address: tuple[str, int] = ("0.0.0.0", 8080),
    *,
    environment: Mapping[str, str] | None = None,
    product_reader: ProductReader | None = None,
) -> ProductHTTPServer:
    settings = os.environ if environment is None else environment
    owner = owner_identity(settings.get("DS60_PRODUCT_OWNER", ""))
    origin = settings.get("DS60_PRODUCT_PUBLIC_ORIGIN", "")
    public_identity(origin)
    token_bytes = read_regular(
        Path(settings.get("DS60_PRODUCT_TOKEN_FILE", "/state/private/token")), 65
    )
    try:
        token = token_bytes.removesuffix(b"\n").decode("ascii")
    except UnicodeError as error:
        raise StateError("Private product token must be ASCII hex") from error
    if HEX.fullmatch(token) is None:
        raise StateError("Private product token must be 64 lowercase ASCII hex characters")
    raw = RawStore(Path(settings.get("DS60_PRODUCT_RAW_DIR", "/state/raw")), owner, writable=True)
    return ProductHTTPServer(
        address,
        raw_store=raw,
        owner=owner,
        token=token,
        public_origin=origin,
        published_directory=Path(settings.get("DS60_PRODUCT_PUBLISHED_DIR", "/state/published")),
        product_reader=product_reader,
    )


def main() -> None:
    server = create_server()
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
