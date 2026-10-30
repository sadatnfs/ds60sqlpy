#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare pinned native source in a fresh directory; downloads require opt-in."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import tarfile
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError
from urllib.request import Request, urlopen

DEPENDENCIES = {
    "TMB_1.9.25.tar.gz": (
        "cf9663b29949cd5eaccb32e11900c9e07caec7d6ac4f17cfd938317dc33acff2",
        (
            "https://cran.r-project.org/src/contrib/TMB_1.9.25.tar.gz",
            "https://cran.r-project.org/src/contrib/Archive/TMB/TMB_1.9.25.tar.gz",
        ),
    ),
    "RcppEigen_0.3.4.0.2.tar.gz": (
        "ecad7ba2129fd48b7ebb825558d38492ed1f3a8934959e27fcd6688175e542bb",
        (
            "https://cran.r-project.org/src/contrib/RcppEigen_0.3.4.0.2.tar.gz",
            "https://cran.r-project.org/src/contrib/Archive/RcppEigen/RcppEigen_0.3.4.0.2.tar.gz",
        ),
    ),
    "json.hpp": (
        "aaf127c04cb31c406e5b04a63f1ae89369fccde6d8fa7cdda1ed4f32dfc5de63",
        (
            "https://raw.githubusercontent.com/nlohmann/json/v3.12.0/single_include/nlohmann/json.hpp",
        ),
    ),
    "nlohmann-LICENSE.MIT": (
        "46a65cffd1ea955132d95a8dd921640714a8d6b537d2e4e482d31145ae95b603",
        ("https://raw.githubusercontent.com/nlohmann/json/v3.12.0/LICENSE.MIT",),
    ),
}
LIMIT = 20_000_000


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def acquire(name: str, cache: Path | None, network: bool) -> bytes:
    expected, urls = DEPENDENCIES[name]
    local = cache / name if cache else None
    if local is not None and local.is_file() and not local.is_symlink():
        if local.stat().st_size > LIMIT:
            raise ValueError(f"Dependency exceeds size limit: {name}")
        result = local.read_bytes()
    elif network:
        result = None
        for url in urls:
            try:
                with urlopen(
                    Request(url, headers={"User-Agent": "spark-tmbad-preparation"}), timeout=60
                ) as response:
                    if not response.geturl().startswith("https://"):
                        raise ValueError("Dependency redirect lost HTTPS")
                    result = response.read(LIMIT + 1)
                break
            except HTTPError as error:
                if error.code != 404:
                    raise RuntimeError(
                        f"Dependency download failed: {name}, HTTP{error.code}"
                    ) from None
        if result is None:
            raise ValueError(f"Pinned dependency unavailable: {name}")
    else:
        raise ValueError(
            f"Supply the verified {name} in --archives or opt in with --allow-download"
        )
    if len(result) > LIMIT or digest(result) != expected:
        raise ValueError(f"Dependency digest mismatch: {name}")
    return result


def extract_headers(data: bytes, prefix: str, destination: Path, limit: int) -> None:
    seen = set()
    total = 0
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for entry in archive:
            if not entry.name.startswith(prefix) or entry.isdir():
                continue
            rel = PurePosixPath(entry.name[len(prefix) :])
            if (
                not entry.isfile()
                or rel.is_absolute()
                or not rel.parts
                or ".." in rel.parts
                or str(rel) in seen
                or entry.size > 2_000_000
                or entry.size < 0
            ):
                raise ValueError("Unexpected dependency archive member")
            seen.add(str(rel))
            total += entry.size
            if len(seen) > limit or total > 40_000_000:
                raise ValueError("Dependency extraction exceeds bounds")
            stream = archive.extractfile(entry)
            if stream is None:
                raise ValueError("Dependency member is missing")
            value = stream.read(entry.size + 1)
            if len(value) != entry.size:
                raise ValueError("Dependency member length changed")
            path = destination.joinpath(*rel.parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
    if not seen:
        raise ValueError("Dependency has no expected headers")


def archive_file(data: bytes, member: str) -> bytes:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        item = archive.getmember(member)
        if not item.isfile() or item.size > 2_000_000:
            raise ValueError("Invalid dependency notice")
        stream = archive.extractfile(item)
        if stream is None:
            raise ValueError("Dependency notice missing")
        return stream.read()


def prepare(destination: Path, cache: Path | None, network: bool) -> None:
    if destination.exists() or destination.is_symlink():
        raise ValueError("Use a fresh SDK destination; existing preparation is never overwritten")
    acquired = {name: acquire(name, cache, network) for name in DEPENDENCIES}
    gpl = Path("/usr/share/common-licenses/GPL-2")
    if not gpl.is_file():
        raise ValueError("Prepare on Linux with the GPL-2 license text installed")
    destination.mkdir(parents=True)
    sources = destination / "sources"
    sources.mkdir()
    notices = destination / "notices"
    notices.mkdir()
    for name, data in acquired.items():
        (sources / name).write_bytes(data)
    extract_headers(
        acquired["TMB_1.9.25.tar.gz"], "TMB/inst/include/TMBad/", destination / "include/TMBad", 64
    )
    extract_headers(
        acquired["RcppEigen_0.3.4.0.2.tar.gz"],
        "RcppEigen/inst/include/",
        destination / "eigen",
        1000,
    )
    (destination / "json").mkdir()
    (destination / "json/json.hpp").write_bytes(acquired["json.hpp"])
    (notices / "nlohmann-LICENSE.MIT").write_bytes(acquired["nlohmann-LICENSE.MIT"])
    shutil.copyfile(gpl, notices / "TMB-GPL-2.txt")
    for archive_name, member, filename in (
        ("TMB_1.9.25.tar.gz", "TMB/DESCRIPTION", "TMB-DESCRIPTION"),
        ("RcppEigen_0.3.4.0.2.tar.gz", "RcppEigen/DESCRIPTION", "RcppEigen-DESCRIPTION"),
        ("RcppEigen_0.3.4.0.2.tar.gz", "RcppEigen/LICENSE", "RcppEigen-LICENSE"),
        ("RcppEigen_0.3.4.0.2.tar.gz", "RcppEigen/inst/COPYRIGHTS", "RcppEigen-COPYRIGHTS"),
    ):
        (notices / filename).write_bytes(archive_file(acquired[archive_name], member))
    inventory = {
        str(p.relative_to(destination)): digest(p.read_bytes())
        for p in sorted(destination.rglob("*"))
        if p.is_file()
    }
    (destination / "sdk.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "dependencies": {n: d[0] for n, d in DEPENDENCIES.items()},
                "files": inventory,
                "r_runtime_required": False,
                "notice": (
                    "Original sources MIT; native TMBad dependency GPL-2; "
                    "preserve corresponding sources and notices."
                ),
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--destination", type=Path, required=True)
    p.add_argument("--archives", type=Path)
    p.add_argument("--allow-download", action="store_true")
    a = p.parse_args()
    prepare(a.destination.absolute(), a.archives, a.allow_download)
