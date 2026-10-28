"""Install reviewed upstream releases and verify every downloaded archive."""

import hashlib
import io
import os
import tarfile
import urllib.request
import zipfile
from pathlib import Path

SCALAFMT = {
    "amd64": (
        "x86_64",
        "7b0e44cc193eeff06daa14b394dc0489d8eaa4537eb945522f7f267641ed8c2b",
    ),
    "arm64": (
        "aarch64",
        "691576a60e00f4bca150d251395196a382f0828697a9b1b4c9c44815eaea80bc",
    ),
}


def download(url: str, expected: str) -> bytes:
    """Verify bytes before interpreting the archive contents."""
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError(f"Checksum mismatch: {url}")
    return data


def main() -> None:
    arch, checksum = SCALAFMT[os.environ["TARGETARCH"]]
    data = download(
        "https://github.com/scalameta/scalafmt/releases/download/v3.11.5/"
        f"scalafmt-{arch}-pc-linux.zip",
        checksum,
    )
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = [name for name in archive.namelist() if Path(name).name == "scalafmt"]
        if len(names) != 1:
            raise RuntimeError("Expected one scalafmt executable")
        executable = Path("/usr/local/bin/scalafmt")
        executable.write_bytes(archive.read(names[0]))
        executable.chmod(0o755)

    # Keep the native compiler pin aligned with docker/workers/native/releases.lock.json.
    stan_release = {
        "amd64": (
            "cmdstan-2.40.0.tar.gz",
            "26d21c9737b35728e926f9b7a5d7362b38dc23e2e7d5e166c890e1fa74dac90c",
        ),
        "arm64": (
            "cmdstan-2.40.0-linux-arm64.tar.gz",
            "c31e9f45a701c47f547381080ee804bf7e2428aace68eff68d4262b5c406aa63",
        ),
    }
    filename, checksum = stan_release[os.environ["TARGETARCH"]]
    data = download(
        "https://github.com/stan-dev/cmdstan/releases/download/v2.40.0/" + filename, checksum
    )
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        stream = archive.extractfile("cmdstan-2.40.0/bin/linux-stanc")
        if stream is None:
            raise RuntimeError("Missing pinned Stan compiler")
        target = Path("/usr/local/bin/stanc")
        target.write_bytes(stream.read())
        target.chmod(0o755)

    data = download(
        "https://codeload.github.com/darold/pgFormatter/tar.gz/refs/tags/v5.11",
        "563619e13294b3db55d7a98a761786024ea3609d007fa94654a69a7346b8fd67",
    )
    destination = Path("/opt/pgFormatter")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            relative = Path(*Path(member.name).parts[1:])
            if not member.isfile() or ".." in relative.parts:
                continue
            if relative != Path("pg_format") and relative.parts[:1] != ("lib",):
                continue
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"Missing archive member: {member.name}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read())
    (destination / "pg_format").chmod(0o755)
    Path("/usr/local/bin/pg_format").symlink_to(destination / "pg_format")


if __name__ == "__main__":
    main()
