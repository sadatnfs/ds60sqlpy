"""Tiny offline workload; no cluster token, shell, upload or external data API."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

VERSION = "ds60-fixture-v1"


class FixtureHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        responses = {"/ready": b"ready\n", "/version": (VERSION + "\n").encode()}
        body = responses.get(self.path, b"not found\n")
        self.send_response(200 if self.path in responses else 404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def check_version(url: str, expected: str) -> bool:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in ("hello", "127.0.0.1", "localhost")
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != "/version"
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Only the bounded local version fixture endpoint is supported.")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("server")
    client = commands.add_parser("client")
    client.add_argument("--url", required=True)
    client.add_argument("--expect", required=True)
    args = parser.parse_args(argv)
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
    except ValueError:
        passed = False
    print(
        "CHECK_OK version=" + VERSION if passed else "CHECK_FAILED version response did not match",
        flush=True,
    )
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
