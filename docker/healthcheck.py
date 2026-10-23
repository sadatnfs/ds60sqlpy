#!/usr/bin/env python3
"""Check the fixed local application endpoint without forwarding proxy settings."""

from __future__ import annotations

import os
from urllib.request import ProxyHandler, Request, build_opener

try:
    port = int(os.environ.get("DS60_LAB_PORT", "8765"))
    public_port = int(os.environ.get("DS60_PUBLIC_PORT") or port)
    if not 1 <= port <= 65535 or not 1 <= public_port <= 65535:
        raise ValueError("Invalid application port")
    opener = build_opener(ProxyHandler({}))
    request = Request(
        f"http://127.0.0.1:{port}/learn", headers={"Host": f"127.0.0.1:{public_port}"}
    )
    with opener.open(request, timeout=2) as response:
        if response.status != 200:
            raise OSError("Application is not ready")
        response.read(1_000_000)
except (OSError, ValueError):
    raise SystemExit(1) from None
