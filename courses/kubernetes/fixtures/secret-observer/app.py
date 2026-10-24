"""Observe only two public teaching markers; never return marker bytes."""

from __future__ import annotations

import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MARKERS = {b"DUMMY_LESSON_ONLY": "initial", b"DUMMY_LESSON_ROTATED": "rotated"}


def marker_label(path: Path) -> str:
    with path.open("rb") as stream:
        value = stream.read(65)
    if value not in MARKERS:
        raise ValueError("Only the two public teaching markers are accepted")
    return MARKERS[value]


class Observation:
    def __init__(self, path: Path, environment: str, pod_uid: str) -> None:
        encoded = environment.encode("ascii")
        if encoded not in MARKERS:
            raise ValueError("A public teaching environment marker is required")
        self.path = path
        self.environment = MARKERS[encoded]
        self.cached = marker_label(path)
        self.pod_uid = pod_uid
        self.boot_id = uuid.uuid4().hex
        self.lock = threading.Lock()

    def _snapshot(self, projected: str) -> dict[str, str]:
        return {
            "pod_uid": self.pod_uid,
            "boot_id": self.boot_id,
            "environment": self.environment,
            "projected_file": projected,
            "application_cache": self.cached,
        }

    def observe(self) -> dict[str, str]:
        with self.lock:
            return self._snapshot(marker_label(self.path))

    def reload(self) -> dict[str, str]:
        with self.lock:
            projected = marker_label(self.path)
            self.cached = projected
            return self._snapshot(projected)


def handler_for(observation: Observation) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

        def send_json(self, status: int, value: dict[str, str]) -> None:
            content = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self) -> None:
            if self.path not in ("/observe", "/ready"):
                self.send_json(404, {"error": "Unknown teaching endpoint"})
                return
            try:
                self.send_json(200, observation.observe())
            except (OSError, ValueError):
                self.send_json(503, {"error": "Synthetic marker unavailable or invalid"})

        def do_POST(self) -> None:
            if self.path != "/reload":
                self.send_json(404, {"error": "Unknown teaching endpoint"})
                return
            if self.headers.get_all("Transfer-Encoding") is not None or self.headers.get_all(
                "Content-Length", ["0"]
            ) != ["0"]:
                self.send_json(400, {"error": "Reload accepts no request body"})
                return
            try:
                self.send_json(200, observation.reload())
            except (OSError, ValueError):
                self.send_json(503, {"error": "Synthetic marker unavailable or invalid"})

    return Handler


def main() -> None:
    observation = Observation(
        Path("/synthetic/message"),
        os.environ["SYNTHETIC_MARKER"],
        os.environ["POD_UID"],
    )
    with ThreadingHTTPServer(("0.0.0.0", 8080), handler_for(observation)) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
