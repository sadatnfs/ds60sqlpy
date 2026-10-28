"""Install a pinned native toolchain after validating its complete archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
import tempfile
import urllib.request
from pathlib import Path

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
        urllib.request.urlopen(asset["url"], timeout=120) as response,
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
