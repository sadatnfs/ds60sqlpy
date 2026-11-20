"""Download one SHA-256 pinned file during an image build, retrying brief throttling."""

from __future__ import annotations

import hashlib
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MAX_BYTES = 64 * 1024 * 1024


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


def main(arguments: list[str]) -> int:
    if len(arguments) != 3:
        print("Usage: fetch_pinned.py URL SHA256 DESTINATION", file=sys.stderr)
        return 2
    url, expected, destination = arguments
    with open_download(url, 60) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or hashlib.sha256(data).hexdigest() != expected:
        print(f"Pinned download size or SHA-256 mismatch: {url}", file=sys.stderr)
        return 1
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as output:
        output.write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
