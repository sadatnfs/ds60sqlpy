"""Install the checksum-pinned official Pinot binary distribution at build time."""

from __future__ import annotations

import hashlib
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path, PurePosixPath

URL = "https://downloads.apache.org/pinot/apache-pinot-1.5.1/apache-pinot-1.5.1-bin.tar.gz"
SHA512 = (
    "0224b13b62e3a7a16f1409081526e07cb35143616d8b3563e2936de82128aaf09"
    "d785bd105b11d221f48784b3031f239fbf969cd53f410243e315cebee034dfa"
)
EXPECTED_BYTES = 857_203_581
MAX_DOWNLOAD = 870_000_000
MAX_EXPANDED = 1_800_000_000


def install(destination: Path = Path("/opt/pinot")) -> None:
    if destination.exists():
        raise ValueError("Destination already exists")
    with tempfile.TemporaryDirectory(prefix="pinot-verified-") as temporary:
        root = Path(temporary)
        archive = root / "pinot.tgz"
        digest = hashlib.sha512()
        size = 0
        with urllib.request.urlopen(URL, timeout=60) as response, archive.open("wb") as output:
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
