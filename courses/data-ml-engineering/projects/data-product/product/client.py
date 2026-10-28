"""Header-authenticated real HTTP client with no redirects, proxies or retries."""

from __future__ import annotations

import argparse
import os
import re
import urllib.error
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .contracts import (
    HEX,
    MAX_BODY,
    ContractError,
    StateError,
    canonical,
    identifier,
    read_regular,
    strict_json,
)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        raise ContractError("The private client never forwards credentials to a redirect")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("status", "product", "snapshots"):
        sub.add_parser(name)
    sub.add_parser("snapshot").add_argument("batch_id")
    sub.add_parser("ingest").add_argument("fixture")
    args = parser.parse_args()
    batch = None
    try:
        base = os.environ.get("DS60_PRODUCT_BASE_URL", "http://api:8080")
        target = urlsplit(base)
        origin = os.environ["DS60_PRODUCT_PUBLIC_ORIGIN"]
        public = urlsplit(origin)
        if (
            (target.scheme, target.hostname, target.port, target.path) != ("http", "api", 8080, "")
            or target.username
            or target.password
            or target.query
            or target.fragment
        ):
            raise ContractError("The private client requires the owned internal API endpoint")
        if (
            public.scheme != "http"
            or public.hostname != "127.0.0.1"
            or public.port is None
            or public.path
            or public.query
            or public.fragment
            or public.username
            or public.password
        ):
            raise ContractError("Use the saved loopback public origin")
        token = (
            read_regular(
                Path(os.environ.get("DS60_PRODUCT_TOKEN_FILE", "/state/private/token")), 100
            )
            .decode()
            .strip()
        )
        if HEX.fullmatch(token) is None:
            raise StateError("Saved client token is malformed")
        route = {
            "status": "/api/status",
            "product": "/api/product",
            "snapshots": "/api/snapshots",
        }.get(args.action)
        body = None
        if args.action == "snapshot":
            batch = identifier(args.batch_id, "Batch identity")
            route = "/api/snapshots/" + batch
        elif args.action == "ingest":
            if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\.json", args.fixture) is None:
                raise ContractError(
                    "Choose one JSON filename inside this project's fixtures directory"
                )
            body = read_regular(Path("/fixtures") / args.fixture, MAX_BODY)
            parsed = strict_json(body)
            if type(parsed) is dict:
                batch = parsed.get("batch_id")
            route = "/api/snapshots"
        headers = {"Host": public.netloc, "Origin": origin, "X-DS60-Product-Token": token}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(base + str(route), data=body, headers=headers)
        opener = build_opener(ProxyHandler({}), NoRedirect())
        try:
            with opener.open(request, timeout=10) as response:
                result = strict_json(response.read(MAX_BODY + 1))
                print(canonical(result).decode())
                return 0
        except urllib.error.HTTPError as error:
            result = strict_json(error.read(MAX_BODY + 1))
            print(canonical({"http_status": error.code, "response": result}).decode())
            return 2
    except (
        ContractError,
        StateError,
        KeyError,
        UnicodeError,
        OSError,
        urllib.error.URLError,
    ) as error:
        print(
            canonical(
                {
                    "error": type(error).__name__,
                    "message": str(error),
                    "automatic_retry": False,
                    "reconcile_batch_identity": batch,
                }
            ).decode()
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
