"""Prepare only the checked TMBad source, retaining its original archive/license."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request

VERSION = "1.9.25"
SHA256 = "cf9663b29949cd5eaccb32e11900c9e07caec7d6ac4f17cfd938317dc33acff2"
URLS = (
    f"https://cran.r-project.org/src/contrib/TMB_{VERSION}.tar.gz",
    f"https://cran.r-project.org/src/contrib/Archive/TMB/TMB_{VERSION}.tar.gz",
)


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


def prepare(destination: Path) -> None:
    body = None
    origin = ""
    for url in URLS:
        try:
            with open_download(
                Request(url, headers={"User-Agent": "DS60-native-AD-probe"}), 60
            ) as response:
                if not response.geturl().startswith("https://"):
                    raise ValueError("dependency download lost HTTPS")
                body = response.read(20_000_001)
            origin = url
            break
        except HTTPError as error:
            if error.code != 404:
                raise
    if body is None or len(body) > 20_000_000 or hashlib.sha256(body).hexdigest() != SHA256:
        raise ValueError("the pinned TMB source archive is unavailable or has different bytes")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / f"TMB_{VERSION}.tar.gz").write_bytes(body)
    prefix = "TMB/inst/include/TMBad/"
    written = []
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
        for member in archive.getmembers():
            if not member.name.startswith(prefix):
                continue
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError("unexpected link in the native dependency")
            relative = Path(member.name[len("TMB/inst/include/") :])
            if relative.is_absolute() or ".." in relative.parts or member.size > 2_000_000:
                raise ValueError("unexpected native dependency member")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("missing dependency bytes")
            path = destination / "include" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(stream.read())
            written.append(relative.as_posix())
        description = archive.extractfile("TMB/DESCRIPTION")
        if description is None:
            raise ValueError("dependency package description is missing")
        (destination / "TMB-DESCRIPTION").write_bytes(description.read())
    if not 1 <= len(written) <= 64:
        raise ValueError("unexpected native dependency layout")

    eigen_version = "0.3.4.0.2"
    eigen_digest = "ecad7ba2129fd48b7ebb825558d38492ed1f3a8934959e27fcd6688175e542bb"
    eigen_body = None
    for eigen_url in (
        f"https://cran.r-project.org/src/contrib/RcppEigen_{eigen_version}.tar.gz",
        f"https://cran.r-project.org/src/contrib/Archive/RcppEigen/RcppEigen_{eigen_version}.tar.gz",
    ):
        try:
            with open_download(eigen_url, 60) as response:
                if not response.geturl().startswith("https://"):
                    raise ValueError("Eigen download lost HTTPS")
                eigen_body = response.read(20_000_001)
            break
        except HTTPError as error:
            if error.code != 404:
                raise
    if (
        eigen_body is None
        or len(eigen_body) > 20_000_000
        or hashlib.sha256(eigen_body).hexdigest() != eigen_digest
    ):
        raise ValueError("the pinned Eigen header archive has different bytes")
    (destination / f"RcppEigen_{eigen_version}.tar.gz").write_bytes(eigen_body)
    eigen_files = []
    with tarfile.open(fileobj=io.BytesIO(eigen_body), mode="r:gz") as archive:
        prefix = "RcppEigen/inst/include/"
        for member in archive.getmembers():
            if not member.name.startswith(prefix) or member.isdir():
                continue
            if not member.isfile():
                raise ValueError("unexpected link in Eigen dependency")
            relative = Path(member.name[len(prefix) :])
            if relative.is_absolute() or ".." in relative.parts or member.size > 2_000_000:
                raise ValueError("unexpected Eigen dependency member")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("missing Eigen header bytes")
            path = destination / "eigen" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(stream.read())
            eigen_files.append(relative.as_posix())
        for member_name, local_name in (
            ("RcppEigen/DESCRIPTION", "RcppEigen-DESCRIPTION"),
            ("RcppEigen/LICENSE", "RcppEigen-LICENSE"),
            ("RcppEigen/inst/COPYRIGHTS", "RcppEigen-COPYRIGHTS"),
        ):
            stream = archive.extractfile(member_name)
            if stream is None:
                raise ValueError("Eigen license metadata is missing")
            (destination / local_name).write_bytes(stream.read())
    if not 1 <= len(eigen_files) <= 1000:
        raise ValueError("unexpected Eigen header layout")
    (destination / "eigen-source.json").write_text(
        json.dumps(
            {
                "package": "RcppEigen",
                "version": eigen_version,
                "archive_sha256": eigen_digest,
                "used_component": "Eigen C++ headers",
                "r_package_installed": False,
                "files": eigen_files,
            },
            indent=2,
        )
        + "\n"
    )

    shutil.copyfile("/usr/share/common-licenses/GPL-2", destination / "TMB-GPL-2.txt")
    (destination / "source.json").write_text(
        json.dumps(
            {
                "package": "TMB",
                "version": VERSION,
                "url": origin,
                "archive_sha256": SHA256,
                "component": "TMBad",
                "files": written,
                "dependency_license": "GPL-2",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: prepare_sdk.py DESTINATION")
    prepare(Path(sys.argv[1]))
