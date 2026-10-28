"""Prepare hash-locked native wheels with no runtime package downloads."""

from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
import urllib.request
from pathlib import Path

PIP_URL = (
    "https://files.pythonhosted.org/packages/44/3c/"
    "d717024885424591d5376220b5e836c2d5293ce2011523c9de23ff7bf068/"
    "pip-25.3-py3-none-any.whl"
)
PIP_SHA256 = "9655943313a94722b7774661c21049070f6bbb0a1516bf02f7c8d5d9201514cd"


def prepare() -> None:
    arch = {"aarch64": "arm64", "x86_64": "amd64"}.get(platform.machine())
    libc, version = platform.libc_ver()
    if arch is None or libc != "glibc" or tuple(map(int, version.split(".")[:2])) < (2, 39):
        raise ValueError("Use native Linux AMD64/ARM64 with glibc2.39 or later")
    if sys.version_info[:2] != (3, 12):
        raise ValueError("This prepared lock targets Python3.12")
    with urllib.request.urlopen(PIP_URL, timeout=60) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000 or hashlib.sha256(data).hexdigest() != PIP_SHA256:
        raise ValueError("Pip preparation wheel identity mismatch")
    wheel = Path("/tmp/pip-25.3-py3-none-any.whl")
    wheel.write_bytes(data)
    command = (
        "import sys; sys.path.insert(0, sys.argv.pop(1)); "
        "from pip._internal.cli.main import main; raise SystemExit(main())"
    )
    subprocess.run(
        [
            sys.executable,
            "-c",
            command,
            str(wheel),
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "--no-compile",
            "--only-binary=:all:",
            "--require-hashes",
            "--target",
            "/opt/ballista",
            "-r",
            str(Path(__file__).with_name(f"requirements.{arch}.lock")),
        ],
        check=True,
        timeout=600,
    )
    wheel.unlink()


if __name__ == "__main__":
    prepare()
