"""Install a topologically ordered, SHA-256 locked CRAN source closure at build time."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

lock = json.loads(Path("/tmp/r-packages.lock.json").read_text())
if lock["schema_version"] != 1:
    raise ValueError("Unknown R dependency lock")
with tempfile.TemporaryDirectory(prefix="cran-") as scratch:
    for package in lock["packages"]:
        data = None
        for key in ("url", "archive_url"):
            url = package[key]
            if not url.startswith("https://cloud.r-project.org/src/contrib/"):
                raise ValueError("Unreviewed R package host")
            try:
                with urllib.request.urlopen(url, timeout=120) as response:
                    data = response.read(80_000_001)
                break
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise
        if (
            data is None
            or len(data) > 80_000_000
            or hashlib.sha256(data).hexdigest() != package["sha256"]
        ):
            raise ValueError("R package archive failed integrity verification: " + package["name"])
        target = Path(scratch) / (package["name"] + "_" + package["version"] + ".tar.gz")
        target.write_bytes(data)
        print("Installing locked package", package["name"], package["version"], flush=True)
        subprocess.run(["R", "CMD", "INSTALL", "--no-docs", "--no-html", str(target)], check=True)
        target.unlink()
subprocess.run(
    ["Rscript", "--vanilla", "-e", 'stopifnot(getRversion() == "' + lock["r_version"] + '")'],
    check=True,
)
