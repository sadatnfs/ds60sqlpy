"""Prepare one exact official runtime after checksum and archive-path validation."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

LOCK = json.loads(Path(__file__).with_name("artifact-lock.json").read_text())


def install(target: Path) -> None:
    if target.exists() or target.is_symlink():
        raise ValueError("Runtime destination must be absent; existing data is retained")
    runtime = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True)
    compiler = subprocess.check_output(["javac", "-version"], stderr=subprocess.STDOUT, text=True)
    if 'version "17.' not in runtime or not compiler.startswith("javac 17."):
        raise ValueError("Use the reviewed native Java17 runtime/compiler before downloading")
    with tempfile.TemporaryDirectory(prefix="flink-prepare-") as temporary:
        archive = Path(temporary) / "runtime.tgz"
        digest = hashlib.sha512()
        total = 0
        with (
            urllib.request.urlopen(LOCK["url"], timeout=60) as response,
            archive.open("xb") as output,
        ):
            parsed = urlsplit(response.geturl())
            if parsed.scheme != "https" or parsed.hostname not in {
                "downloads.apache.org",
                "dlcdn.apache.org",
                "archive.apache.org",
            }:
                raise ValueError("Unexpected distribution redirect")
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > LOCK["archive_bytes"]:
                    raise ValueError("Distribution exceeds the reviewed byte bound")
                digest.update(chunk)
                output.write(chunk)
                if total // 50_000_000 != (total - len(chunk)) // 50_000_000:
                    print(
                        f"Downloaded {total:,} of {LOCK['archive_bytes']:,} verified-release bytes",
                        flush=True,
                    )
        if total != LOCK["archive_bytes"] or digest.hexdigest() != LOCK["sha512"]:
            raise ValueError("Official distribution byte count or SHA512 differs")
        print("Official Flink distribution size and SHA512 verified", flush=True)
        unpack = Path(temporary) / "unpack"
        unpack.mkdir()
        with tarfile.open(archive, "r:gz") as package:
            members = package.getmembers()
            if len(members) > 30_000 or sum(member.size for member in members) > 2_500_000_000:
                raise ValueError("Distribution extraction exceeds its reviewed bound")
            for member in members:
                member_path = PurePosixPath(member.name)
                if (
                    member_path.is_absolute()
                    or ".." in member_path.parts
                    or not member_path.parts
                    or member_path.parts[0] != "flink-2.3.0"
                    or len(member.name) > 1024
                ):
                    raise ValueError("Unsafe distribution path")
                if not (member.isfile() or member.isdir()) or member.size > 700_000_000:
                    raise ValueError("Unsupported distribution member")
            package.extractall(unpack, members=members, filter="data")
        staged = unpack / "flink-2.3.0"
        for required in ("bin/flink", "bin/jobmanager.sh", "bin/taskmanager.sh", "lib", "conf"):
            if not (staged / required).exists():
                raise ValueError("Runtime distribution is incomplete")
        shutil.move(str(staged), target)
        for path in [target, *target.rglob("*")]:
            if path.is_symlink():
                raise ValueError("Unexpected installed symbolic link")
            executable = (
                path.is_dir()
                or (path.parent == target / "bin" and path.suffix == ".sh")
                or path == target / "bin/flink"
            )
            path.chmod(0o755 if executable else 0o644)
        (target / "DS60-PREPARATION.json").write_text(json.dumps(LOCK, indent=2) + "\n")
        print("Prepared runtime; no dependency download occurs during a lesson", flush=True)


if __name__ == "__main__":
    install(Path("/opt/flink"))
