"""Explicit serial preparation of the optional, independently locked R reference."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
BASE_PACKAGES = {
    "R",
    "base",
    "compiler",
    "datasets",
    "graphics",
    "grDevices",
    "grid",
    "methods",
    "parallel",
    "splines",
    "stats",
    "stats4",
    "tcltk",
    "tools",
    "utils",
}
MAX_ARCHIVE = 80_000_000


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def version(value):
    return tuple(int(part) for part in re.split(r"[.-]", value))


def dependency_constraints(value):
    for entry in value.split(","):
        if not entry.strip():
            continue
        match = re.fullmatch(
            r"\s*([A-Za-z][A-Za-z0-9.]*)\s*(?:\((>=|<=|==|>|<)\s*([0-9.-]+)\))?\s*", entry
        )
        if match is None:
            raise ValueError("Unsupported dependency constraint in the reviewed lock")
        yield match.groups()


def validate_lock(lock):
    if lock.get("schema_version") != 1 or lock.get("r_version") != "4.6.1":
        raise ValueError("Unknown optional reference lock or R version")
    packages = lock["packages"]
    versions = {p["name"]: p["version"] for p in packages}
    if len(versions) != len(packages):
        raise ValueError("Duplicate locked package")
    versions["R"] = lock["r_version"]
    completed = set(BASE_PACKAGES)
    for package in packages:
        if not re.fullmatch(r"[a-f0-9]{64}", package["sha256"]):
            raise ValueError("Every archive requires a SHA256")
        for field in ["Depends", "Imports", "LinkingTo"]:
            for name, operator, minimum in dependency_constraints(package["dependencies"][field]):
                if name not in completed:
                    raise ValueError(
                        "Lock is not a complete topological dependency closure: " + name
                    )
                if operator and name in versions:
                    actual, required = version(versions[name]), version(minimum)
                    accepted = {
                        ">=": actual >= required,
                        "<=": actual <= required,
                        "==": actual == required,
                        ">": actual > required,
                        "<": actual < required,
                    }[operator]
                    if not accepted:
                        raise ValueError("Locked dependency constraint is incompatible: " + name)
        completed.add(package["name"])
    if lock["upstream"]["revision"] != "1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c":
        raise ValueError("Unreviewed upstream revision")


def acquire(entry, filename, archives, destination, allow_download):
    candidate = archives / filename if archives else None
    if candidate and candidate.is_file() and not candidate.is_symlink():
        if candidate.stat().st_size > MAX_ARCHIVE:
            raise ValueError("Cached source exceeds archive bound")
        data = candidate.read_bytes()
    elif allow_download:
        data = None
        for url in dict.fromkeys([entry["url"], entry.get("archive_url", entry["url"])]):
            if not url.startswith(
                (
                    "https://cran.r-project.org/src/contrib/",
                    "https://codeload.github.com/glmmTMB/glmmTMB/tar.gz/",
                )
            ):
                raise ValueError("Unreviewed source origin")
            for attempt in range(5):
                try:
                    request = urllib.request.Request(
                        url, headers={"User-Agent": "DS60-optional-reference-preparation"}
                    )
                    with urllib.request.urlopen(request, timeout=90) as response:
                        data = response.read(MAX_ARCHIVE + 1)
                    break
                except urllib.error.HTTPError as error:
                    if error.code == 404:
                        break
                    if error.code not in {429, 500, 502, 503, 504} or attempt == 4:
                        raise RuntimeError(
                            "Source download failed with HTTP" + str(error.code)
                        ) from None
                    time.sleep(min(30, 2 ** (attempt + 1)))
            if data is not None:
                break
        if data is None:
            raise ValueError("Pinned source unavailable: " + filename)
    else:
        raise ValueError("Supply the pinned archive or explicitly allow downloads: " + filename)
    if len(data) > MAX_ARCHIVE or hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError("Pinned source hash/size mismatch: " + filename)
    destination.write_bytes(data)
    return destination


def unpack_package(archive_path, prefix, output):
    count, total = 0, 0
    with tarfile.open(archive_path) as archive:
        for member in archive:
            if not member.name.startswith(prefix) or member.isdir():
                continue
            relative = PurePosixPath(member.name[len(prefix) :])
            if (
                not member.isfile()
                or relative.is_absolute()
                or ".." in relative.parts
                or not relative.parts
            ):
                raise ValueError("Unsafe upstream source archive member")
            count += 1
            total += member.size
            if count > 10000 or total > 200_000_000 or member.size < 0 or member.size > 30_000_000:
                raise ValueError("Upstream package extraction exceeds bounds")
            target = output.joinpath(*relative.parts)
            if target.exists():
                raise ValueError("Duplicate upstream archive member")
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("Upstream archive member missing")
            target.write_bytes(stream.read(member.size + 1))
    if not count:
        raise ValueError("Pinned upstream package subtree missing")


def logged(command, path, environment, timeout=3600):
    print("Preparing", path.stem, flush=True)
    with tempfile_log(path) as log:
        result = subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=environment,
            timeout=timeout,
            check=False,
        )
    if result.returncode:
        with gzip.open(path, "rt", errors="replace") as stream:
            text = stream.read()
        print(text[-24000:], flush=True)
        raise RuntimeError("Preparation failed; complete log retained at " + str(path))


class tempfile_log:
    def __init__(self, destination):
        self.destination = destination
        self.raw = destination.with_suffix("")

    def __enter__(self):
        self.stream = self.raw.open("wb")
        return self.stream

    def __exit__(self, *_args):
        self.stream.close()
        with self.raw.open("rb") as source, gzip.open(self.destination, "wb") as output:
            shutil.copyfileobj(source, output)
        self.raw.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archives", type=Path)
    parser.add_argument("--allow-download", action="store_true")
    args = parser.parse_args()
    lock = json.loads((ROOT / "dependencies.lock.json").read_text())
    validate_lock(lock)
    if args.output.exists() or args.output.is_symlink():
        raise ValueError("Use a fresh immutable preparation directory")
    observed = subprocess.check_output(
        ["Rscript", "--vanilla", "-e", "cat(as.character(getRversion()))"], text=True
    )
    if observed != lock["r_version"]:
        raise ValueError("Use the exact locked R version")
    output = args.output.resolve()
    output.mkdir(parents=True)
    for name in ["library", "sources", "logs", "upstream"]:
        (output / name).mkdir()
    environment = dict(
        os.environ,
        R_LIBS_USER=str(output / "library"),
        R_LIBS_SITE=str(output / "library"),
        MAKEFLAGS="-j1",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
    )
    for entry in lock["packages"]:
        name = entry["name"] + "_" + entry["version"] + ".tar.gz"
        archive = acquire(
            entry, name, args.archives, output / "sources" / name, args.allow_download
        )
        logged(
            [
                "R",
                "CMD",
                "INSTALL",
                "--no-multiarch",
                "--no-docs",
                "--no-html",
                "--library=" + str(output / "library"),
                str(archive),
            ],
            output / "logs" / (entry["name"] + ".log.gz"),
            environment,
        )
    upstream = lock["upstream"]
    archive = acquire(
        upstream,
        "glmmTMB-" + upstream["revision"] + ".tar.gz",
        args.archives,
        output / "sources/glmmTMB-pinned.tar.gz",
        args.allow_download,
    )
    unpack_package(archive, upstream["package_prefix"], output / "upstream/glmmTMB")
    logged(
        [
            "R",
            "CMD",
            "INSTALL",
            "--no-multiarch",
            "--no-docs",
            "--no-html",
            "--library=" + str(output / "library"),
            str(output / "upstream/glmmTMB"),
        ],
        output / "logs/glmmTMB.log.gz",
        environment,
    )
    logged(
        ["Rscript", "--vanilla", str(ROOT / "R/compile.R"), str(ROOT), str(output / "models")],
        output / "logs/custom-models.log.gz",
        environment,
    )
    compiled = json.loads((output / "models/compile.json").read_text())
    sources = [
        p
        for folder in ["models", "R", "python"]
        for p in (ROOT / folder).rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    ]
    sources += [ROOT / name for name in ["prepare.py", "dependencies.lock.json", "registry.json"]]
    package_files = {}
    for name in compiled["packages"]:
        package_root = output / "library" / name
        package_files[name] = {
            str(p.relative_to(package_root)): digest(p)
            for p in sorted(package_root.rglob("*"))
            if p.is_file()
            and (p.suffix in {".so", ".rdb", ".rdx"} or p.name in {"DESCRIPTION", "NAMESPACE"})
        }
    manifest = {
        "schema_version": 1,
        "kind": "optional-r-tmb-glmmtmb-reference",
        **compiled,
        "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sorted(sources)},
        "package_files": package_files,
        "upstream_revision": upstream["revision"],
        "upstream_archive_sha256": upstream["sha256"],
        "upstream_license": "AGPL-3",
        "scope": "dependency and template preparation only; numerical study acceptance is separate",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    shutil.copy2(ROOT / "NOTICE.md", output / "NOTICE.md")
    print(
        json.dumps({"prepared": str(output), "manifest_sha256": digest(output / "manifest.json")})
    )


if __name__ == "__main__":
    main()
