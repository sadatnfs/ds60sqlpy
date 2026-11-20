"""Install a pinned native toolchain after validating its complete archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tarfile
import tempfile
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


parser = argparse.ArgumentParser()
parser.add_argument("tool", choices=("stan", "julia"))
args = parser.parse_args()
lock = json.loads(Path("/tmp/native-releases.lock.json").read_text())
asset = lock["assets"][os.environ["TARGETARCH"]][args.tool]
destination = Path("/opt/cmdstan" if args.tool == "stan" else "/opt/julia")
with tempfile.TemporaryDirectory(prefix="native-download-") as scratch:
    archive_path = Path(scratch) / "release.tar.gz"
    digest = hashlib.sha256()
    with (
        open_download(asset["url"], 120) as response,
        archive_path.open("wb") as stream,
    ):
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            stream.write(chunk)
    if digest.hexdigest() != asset["sha256"]:
        raise ValueError("Native archive checksum mismatch")
    with tarfile.open(archive_path) as archive:
        archive.extractall(Path(scratch) / "unpacked", filter="data")
    roots = list((Path(scratch) / "unpacked").iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise ValueError("Expected one native release directory")
    roots[0].rename(destination)
print(args.tool, "verified and installed", flush=True)
