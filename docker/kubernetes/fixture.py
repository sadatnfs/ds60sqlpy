"""Synthetic offline fixture contract 2; no cluster token or arbitrary workload API."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

VERSION = "ds60-fixture-v1"  # Preserve the original hello response contract.
CONTRACT_VERSION = 2
START_TIME = time.monotonic()
MESSAGES = {"hello", "reviewer"}
CONFIG_FILE = Path("/config/message")


def fixture_response(path: str) -> tuple[int, bytes]:
    if path == "/ready":
        return 200, b"ready\n"
    if path == "/version":
        return 200, (VERSION + "\n").encode()
    if path == "/live":
        return 200, b"live\n"
    if path == "/startup":
        delay = os.environ.get("DS60_STARTUP_DELAY_SECONDS", "0")
        if delay not in ("0", "3"):
            return 503, b"invalid synthetic startup delay\n"
        ready = time.monotonic() - START_TIME >= int(delay)
        return (200, b"started\n") if ready else (503, b"starting\n")
    if path == "/message":
        message = os.environ.get("DS60_MESSAGE", "hello")
        return (
            (200, (message + "\n").encode())
            if message in MESSAGES
            else (503, b"invalid synthetic message\n")
        )
    if path == "/file-message":
        try:
            with CONFIG_FILE.open("rb") as stream:
                value = stream.read(65)
            if len(value) > 64:
                return 503, b"message file exceeds budget\n"
            message = value.decode("utf-8").strip()
            return (
                (200, (message + "\n").encode())
                if message in MESSAGES
                else (503, b"invalid synthetic file message\n")
            )
        except (OSError, UnicodeDecodeError):
            return 503, b"synthetic message file unavailable\n"
    return 404, b"not found\n"


class FixtureHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        status, body = fixture_response(self.path)
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def _check_response(url: str, expected: str, *, path: str) -> bool:
    parsed = urlsplit(url)
    if (
        path not in ("/version", "/message", "/file-message")
        or parsed.scheme != "http"
        or parsed.hostname not in ("hello", "127.0.0.1", "localhost")
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != path
        or parsed.query
        or parsed.fragment
        or len(expected.encode("utf-8")) > 64
    ):
        raise ValueError("Only the fixed bounded local fixture endpoint is supported.")
    if parsed.port is None or not 1 <= parsed.port <= 65535:
        raise ValueError("Use an explicit bounded fixture port.")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(url, timeout=2) as response:
            body = response.read(257)
            return (
                response.status == 200
                and len(body) <= 256
                and body.decode("utf-8").strip() == expected
            )
    except (OSError, UnicodeDecodeError, urllib.error.URLError):
        return False


def check_version(url: str, expected: str) -> bool:
    """Keep the original public version-only checker and its URL refusal contract."""
    return _check_response(url, expected, path="/version")


def finite_task(outcome: str) -> tuple[int, dict[str, int | str]]:
    if outcome not in ("success", "failure"):
        raise ValueError("Unknown fixed task outcome")
    if outcome == "failure":
        return 2, {"fixture_contract": CONTRACT_VERSION, "status": "injected-failure"}
    rows = ("10", "0", "bad", "-2", "25")
    accepted = [int(value) for value in rows if re.fullmatch(r"[0-9]+", value)]
    return 0, {
        "accepted": len(accepted),
        "rejected": len(rows) - len(accepted),
        "total": sum(accepted),
        "fixture_contract": CONTRACT_VERSION,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("server")
    client = commands.add_parser("client")
    client.add_argument("--url", required=True)
    client.add_argument("--expect", required=True)
    client.add_argument("--expect-message", choices=sorted(MESSAGES))
    client.add_argument("--expect-file-message", choices=sorted(MESSAGES))
    task = commands.add_parser("task")
    task.add_argument("--outcome", choices=("success", "failure"), required=True)
    args = parser.parse_args(argv)
    if args.action == "task":
        status, result = finite_task(args.outcome)
        print(json.dumps(result, sort_keys=True), flush=True)
        return status
    if args.action == "server":
        server = ThreadingHTTPServer(("0.0.0.0", 8080), FixtureHandler)
        try:
            server.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    try:
        passed = check_version(args.url, args.expect)
        parsed = urlsplit(args.url)
        for path, expected in (
            ("/message", args.expect_message),
            ("/file-message", args.expect_file_message),
        ):
            if expected is not None:
                target = urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
                passed = _check_response(target, expected, path=path) and passed
    except ValueError:
        passed = False
    print(
        "CHECK_OK version=" + VERSION if passed else "CHECK_FAILED fixture response did not match",
        flush=True,
    )
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
