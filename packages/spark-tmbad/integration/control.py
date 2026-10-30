"""Bounded in-network fault coordination; no engine socket or host publication."""

from __future__ import annotations

import argparse
import json
import threading
import time
from contextlib import suppress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WORK = Path("/work")
LIMIT = 10000


class Control:
    def __init__(self):
        self.lock = threading.Lock()
        self.events = []
        self.waiters = []
        self.phase = "starting"
        self.server = ThreadingHTTPServer(("0.0.0.0", 8787), self.handler())
        self.server.daemon_threads = True
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.save()

    def save(self):
        temporary = WORK / "control.json.tmp"
        temporary.write_text(
            json.dumps(
                {"phase": self.phase, "waiters": self.waiters, "event_count": len(self.events)}
            )
        )
        temporary.replace(WORK / "control.json")

    def set_phase(self, value):
        with self.lock:
            self.phase = value
            self.save()

    def handler(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                if self.path not in {"/event", "/gate"}:
                    self.send_error(404)
                    return
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    self.send_error(413)
                    return
                event = json.loads(self.rfile.read(length))
                with owner.lock:
                    if len(owner.events) >= LIMIT:
                        self.send_error(507, "Integration event budget exceeded")
                        return
                    owner.events.append(event)
                    if self.path == "/gate" and not (WORK / "release-loss").exists():
                        owner.waiters.append(event)
                    owner.save()
                if self.path == "/gate":
                    deadline = time.monotonic() + 150
                    while not (WORK / "release-loss").exists():
                        if time.monotonic() >= deadline:
                            self.send_error(504, "Host did not release fault gate")
                            return
                        time.sleep(0.1)
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                with suppress(BrokenPipeError):
                    self.wfile.write(b"OK")

        return Handler

    def wait_restored(self):
        self.set_phase("recovery_fit_complete")
        deadline = time.monotonic() + 150
        while not (WORK / "workers-restored").exists():
            if time.monotonic() >= deadline:
                raise TimeoutError("Host did not restore the stopped owned worker")
            time.sleep(0.2)

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        return self.events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["status", "release", "restored"])
    args = parser.parse_args()
    if args.command == "status":
        print((WORK / "control.json").read_text() if (WORK / "control.json").exists() else "{}")
    else:
        (WORK / ("release-loss" if args.command == "release" else "workers-restored")).touch()


if __name__ == "__main__":
    main()
