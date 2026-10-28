"""Install the checksum-pinned official Cassandra binary distribution at build time."""

from __future__ import annotations

import hashlib
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path, PurePosixPath

URL = "https://downloads.apache.org/cassandra/5.0.9/apache-cassandra-5.0.9-bin.tar.gz"
SHA512 = (
    "beaf3df6342ef1a0ccc83fa80214f250b32c35cfbb1af591b00e3fd539eef0915"
    "bc3b89f0e7ae73f6d50cbb03f6075c4e4cf32d3c46ff9c33f745542fcc925df"
)
MAX_DOWNLOAD = 85_000_000
MAX_EXPANDED = 180_000_000


def install(destination: Path = Path("/opt/cassandra")) -> None:
    if destination.exists():
        raise ValueError("Destination already exists")
    with tempfile.TemporaryDirectory(prefix="cassandra-verified-") as temporary:
        root = Path(temporary)
        archive = root / "cassandra.tgz"
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
        if digest.hexdigest() != SHA512:
            raise ValueError("Official Cassandra distribution SHA512 mismatch")
        with tarfile.open(archive, "r:gz") as bundle:
            members = bundle.getmembers()
            if len(members) > 2000 or sum(member.size for member in members) > MAX_EXPANDED:
                raise ValueError("Distribution archive exceeds extraction bounds")
            for member in members:
                path = PurePosixPath(member.name)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or path.parts[0] != "apache-cassandra-5.0.9"
                ):
                    raise ValueError("Unsafe distribution path")
                if not (member.isfile() or member.isdir()):
                    raise ValueError("Distribution contains a link or special entry")
            bundle.extractall(root, members=members, filter="data")
        shutil.move(str(root / "apache-cassandra-5.0.9"), str(destination))
    print("Verified and installed Apache Cassandra 5.0.9 official binary distribution")


if __name__ == "__main__":
    install()
