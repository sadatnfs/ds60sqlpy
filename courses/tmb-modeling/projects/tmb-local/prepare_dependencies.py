"""Build-time only: fetch pinned R sources, verify them, install serially."""

import hashlib
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path


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
            with urllib.request.urlopen(package["url"], timeout=120) as response:
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
