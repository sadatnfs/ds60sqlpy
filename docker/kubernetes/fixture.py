"""Synthetic offline fixture contract 2; no cluster token or arbitrary workload API."""

from __future__ import annotations

import argparse
import errno
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from http.client import HTTPException, HTTPMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import IO
from urllib.parse import urlsplit, urlunsplit

VERSION = "ds60-fixture-v1"  # Preserve the original hello response contract.
CONTRACT_VERSION = 2
START_TIME = time.monotonic()
MESSAGES = {"hello", "reviewer"}
CONFIG_FILE = Path("/config/message")
# One retry budget covers every read in a client invocation. The Kubernetes Job
# deadline remains the outer bound, including scheduling and resolver delays.
CLIENT_BUDGET_SECONDS = 6.0
REQUEST_TIMEOUT_SECONDS = 2.0
RETRY_DELAY_SECONDS = 0.2


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


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: HTTPMessage,
        newurl: str,
    ) -> None:
        # The local endpoint contract does not authorize any secondary URL.
        return None


def _transient_transport(error: BaseException) -> bool:
    reason = error.reason if isinstance(error, urllib.error.URLError) else error
    if isinstance(reason, socket.gaierror):
        return reason.errno in (socket.EAI_AGAIN, socket.EAI_NONAME)
    if isinstance(reason, (TimeoutError, ConnectionError)):
        return True
    return isinstance(reason, OSError) and reason.errno in {
        errno.ECONNABORTED,
        errno.ECONNREFUSED,
        errno.ECONNRESET,
        errno.EHOSTUNREACH,
        errno.ENETUNREACH,
        errno.ETIMEDOUT,
    }


def _check_response(url: str, expected: str, *, path: str, deadline: float | None = None) -> bool:
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
    if deadline is None:
        deadline = time.monotonic() + CLIENT_BUDGET_SECONDS
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    while (remaining := deadline - time.monotonic()) > 0:
        try:
            with opener.open(url, timeout=min(REQUEST_TIMEOUT_SECONDS, remaining)) as response:
                body = response.read(257)
                # A response that violates the fixture contract is a real failure,
                # not a transient transport error to conceal with another request.
                return (
                    response.status == 200
                    and len(body) <= 256
                    and body.decode("utf-8").strip() == expected
                    and time.monotonic() < deadline
                )
        except urllib.error.HTTPError as error:
            error.close()
            if error.code != 503:
                return False
        except (OSError, urllib.error.URLError) as error:
            if not _transient_transport(error):
                return False
        except (UnicodeDecodeError, HTTPException):
            return False
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(RETRY_DELAY_SECONDS, remaining))
    return False


def check_version(url: str, expected: str, *, deadline: float | None = None) -> bool:
    """Keep the original public version-only checker and its URL refusal contract."""
    return _check_response(url, expected, path="/version", deadline=deadline)


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
        deadline = time.monotonic() + CLIENT_BUDGET_SECONDS
        passed = check_version(args.url, args.expect, deadline=deadline)
        parsed = urlsplit(args.url)
        for path, expected in (
            ("/message", args.expect_message),
            ("/file-message", args.expect_file_message),
        ):
            if not passed:
                break
            if expected is not None:
                target = urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
                passed = _check_response(target, expected, path=path, deadline=deadline)
    except ValueError:
        passed = False
    print(
        "CHECK_OK version=" + VERSION if passed else "CHECK_FAILED fixture response did not match",
        flush=True,
    )
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
