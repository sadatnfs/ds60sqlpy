"""Image-build-only official kubectl download with verified SHA256 and size cap."""

from __future__ import annotations

import hashlib
import os
import re
import urllib.request
from pathlib import Path

version = "v1.37.0"
architecture = os.environ.get("TARGETARCH", "")
if architecture not in ("amd64", "arm64"):
    raise SystemExit("Only native Linux amd64/arm64 worker builds are supported.")
url = f"https://dl.k8s.io/release/{version}/bin/linux/{architecture}/kubectl"
with urllib.request.urlopen(url + ".sha256", timeout=30) as response:
    expected = response.read(256).decode("ascii").strip()
if not re.fullmatch(r"[0-9a-f]{64}", expected):
    raise SystemExit("The official checksum response was invalid.")
output = Path("/usr/local/bin/kubectl")
digest = hashlib.sha256()
size = 0
with urllib.request.urlopen(url, timeout=60) as response, output.open("xb") as destination:
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
