"""Install the checksum-pinned official Pinot binary distribution at build time."""

from __future__ import annotations

import hashlib
import shutil
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

# Pinot 1.6.0 replaced 1.5.1 on downloads.apache.org; the Apache archive keeps every release.
URL = "https://archive.apache.org/dist/pinot/apache-pinot-1.5.1/apache-pinot-1.5.1-bin.tar.gz"
SHA512 = (
    "0224b13b62e3a7a16f1409081526e07cb35143616d8b3563e2936de82128aaf09"
    "d785bd105b11d221f48784b3031f239fbf969cd53f410243e315cebee034dfa"
)
EXPECTED_BYTES = 857_203_581
MAX_DOWNLOAD = 870_000_000
MAX_EXPANDED = 1_800_000_000


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


def install(destination: Path = Path("/opt/pinot")) -> None:
    if destination.exists():
        raise ValueError("Destination already exists")
    with tempfile.TemporaryDirectory(prefix="pinot-verified-") as temporary:
        root = Path(temporary)
        archive = root / "pinot.tgz"
        digest = hashlib.sha512()
        size = 0
        with open_download(URL, 60) as response, archive.open("wb") as output:
            if response.geturl() != URL:
                raise ValueError("Unexpected distribution redirect")
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_DOWNLOAD:
                    raise ValueError("Distribution exceeds its reviewed size bound")
                digest.update(chunk)
                output.write(chunk)
        if size != EXPECTED_BYTES or digest.hexdigest() != SHA512:
            raise ValueError("Official Pinot distribution SHA512 mismatch")
        with tarfile.open(archive, "r:gz") as bundle:
            members = bundle.getmembers()
            if len(members) > 20000 or sum(member.size for member in members) > MAX_EXPANDED:
                raise ValueError("Distribution archive exceeds extraction bounds")
            for member in members:
                path = PurePosixPath(member.name)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or path.parts[0] != "apache-pinot-1.5.1-bin"
                ):
                    raise ValueError("Unsafe distribution path")
                if not (member.isfile() or member.isdir()):
                    raise ValueError("Distribution contains a link or special entry")
            bundle.extractall(root, members=members, filter="data")
        shutil.move(str(root / "apache-pinot-1.5.1-bin"), str(destination))
    print("Verified and installed Apache Pinot 1.5.1 official binary distribution")


if __name__ == "__main__":
    install()
