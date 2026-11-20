"""Image-build-only official kubectl download with verified SHA256 and size cap."""

from __future__ import annotations

import hashlib
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def open_download(source: Any, timeout: float, attempts: int = 5) -> Any:
    """Open a pinned download, retrying brief throttling and gateway errors."""
    for attempt in range(attempts):
        try:
            return urllib.request.urlopen(source, timeout=timeout)
        except urllib.error.HTTPError as error:
            if error.code not in {429, 502, 503, 504} or attempt + 1 == attempts:
                raise
            delay = float(min(30, 2 ** (attempt + 1)))
            retry_after = error.headers.get("Retry-After", "") if error.headers else ""
            if retry_after.isdecimal() and len(retry_after) <= 6:
                delay = float(min(60, int(retry_after)))
            print(
                f"Download returned HTTP {error.code}; retrying the same pinned file "
                f"in {delay:g}s (attempt {attempt + 2}/{attempts}).",
                file=sys.stderr,
                flush=True,
            )
            error.close()
            time.sleep(delay)
    raise AssertionError("Unreachable download attempt boundary")


version = "v1.37.0"
architecture = os.environ.get("TARGETARCH", "")
if architecture not in ("amd64", "arm64"):
    raise SystemExit("Only native Linux amd64/arm64 worker builds are supported.")
url = f"https://dl.k8s.io/release/{version}/bin/linux/{architecture}/kubectl"
with open_download(url + ".sha256", 30) as response:
    expected = response.read(256).decode("ascii").strip()
if not re.fullmatch(r"[0-9a-f]{64}", expected):
    raise SystemExit("The official checksum response was invalid.")
output = Path("/usr/local/bin/kubectl")
digest = hashlib.sha256()
size = 0
with open_download(url, 60) as response, output.open("xb") as destination:
    while chunk := response.read(1024 * 1024):
        size += len(chunk)
        if size > 128 * 1024 * 1024:
            raise SystemExit("The kubectl download exceeds the declared size cap.")
        digest.update(chunk)
        destination.write(chunk)
if digest.hexdigest() != expected:
    output.unlink()
    raise SystemExit("The kubectl download failed SHA256 verification.")
output.chmod(0o755)
