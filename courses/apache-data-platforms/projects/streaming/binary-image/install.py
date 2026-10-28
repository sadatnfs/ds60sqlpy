"""Install the checksum-pinned official Kafka binary distribution at build time."""

from __future__ import annotations

import hashlib
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path, PurePosixPath

URL = "https://downloads.apache.org/kafka/4.4.0/kafka_2.13-4.4.0.tgz"
SHA512 = (
    "f5ceba8a265ab6bb2d68362b1f6859a95e15d60ef92ba83b43fdf065b557dc18"
    "e98d6383c15b9977320e25b3a2c8b6f11decb17b0fa6c0f163423793a0eb95cb"
)
MAX_DOWNLOAD = 150_000_000
MAX_EXPANDED = 300_000_000


def install(destination: Path = Path("/opt/kafka")) -> None:
    if destination.exists():
        raise ValueError("Destination already exists")
    with tempfile.TemporaryDirectory(prefix="kafka-verified-") as temporary:
        root = Path(temporary)
        archive = root / "kafka.tgz"
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
            raise ValueError("Official Kafka distribution SHA512 mismatch")
        with tarfile.open(archive, "r:gz") as bundle:
            members = bundle.getmembers()
            if len(members) > 2000 or sum(member.size for member in members) > MAX_EXPANDED:
                raise ValueError("Distribution archive exceeds extraction bounds")
            for member in members:
                path = PurePosixPath(member.name)
                if path.is_absolute() or ".." in path.parts or path.parts[0] != "kafka_2.13-4.4.0":
                    raise ValueError("Unsafe distribution path")
                if not (member.isfile() or member.isdir()):
                    raise ValueError("Distribution contains a link or special entry")
            bundle.extractall(root, members=members, filter="data")
        shutil.move(str(root / "kafka_2.13-4.4.0"), str(destination))
    print("Verified and installed Apache Kafka 4.4.0 official binary distribution")


if __name__ == "__main__":
    install()
