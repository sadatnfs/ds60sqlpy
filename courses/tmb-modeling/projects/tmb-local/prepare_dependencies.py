"""Build-time only: fetch pinned R sources, verify them, install serially."""

import hashlib
import json
import subprocess
import sys
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


def main():
    lock = json.loads(Path(__file__).with_name("dependencies.lock.json").read_text())
    expected = [lock["r_version"], lock["matrix_version"], lock["rcpp_version"]]
    code = (
        'cat(as.character(getRversion()),as.character(packageVersion("Matrix")),'
        'as.character(packageVersion("Rcpp")),sep="\\n")'
    )
    actual = subprocess.check_output(["Rscript", "--vanilla", "-e", code], text=True).splitlines()
    if actual != expected:
        raise RuntimeError(f"Incompatible base: expected R/Matrix/Rcpp {expected}, got {actual}")
    with tempfile.TemporaryDirectory(prefix="tmb-sources-") as temporary:
        for package in lock["packages"]:
            archive = Path(temporary) / f"{package['name']}_{package['version']}.tar.gz"
            with open_download(package["url"], 120) as response:
                payload = response.read(20_000_001)
            if (
                len(payload) > 20_000_000
                or hashlib.sha256(payload).hexdigest() != package["sha256"]
            ):
                raise RuntimeError(f"Source digest mismatch for {package['name']}")
            archive.write_bytes(payload)
            subprocess.run(
                ["R", "CMD", "INSTALL", "--no-multiarch", str(archive)], check=True, timeout=1800
            )


if __name__ == "__main__":
    main()
