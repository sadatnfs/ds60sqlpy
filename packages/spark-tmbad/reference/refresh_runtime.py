"""Refresh explicitly declared R controllers without rebuilding prepared artifacts.

This local, offline operation writes a fresh directory. Its receipt proves source
admission and immutable artifact reuse, not numerical or distributed acceptance.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
import re
import resource
import shutil
import signal
import stat
import subprocess
import tarfile
import time
from contextlib import suppress
from pathlib import Path, PurePosixPath
from typing import Any

KIND = "optional-r-tmb-glmmtmb-reference"
BASE_INVENTORY = ["prepare.py", "dependencies.lock.json", "registry.json"]
EXTRA_INVENTORY = ["refresh_runtime.py", "tests/pure.R"]
MAX_JSON = 4 * 1024 * 1024
MAX_FILE = 1024 * 1024 * 1024
MAX_TOTAL = 8 * 1024 * 1024 * 1024
MAX_FILES = 100_000
MAX_LOG = 2 * 1024 * 1024
SOURCE_LIMIT = 64 * 1024 * 1024
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
NAME = re.compile(r"[A-Za-z][A-Za-z0-9_.]*\Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def relative(value: str) -> str:
    require(isinstance(value, str) and bool(value), "Empty relative path")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and path.as_posix() == value
        and all(part not in {".", ".."} for part in path.parts)
        and "\\" not in value
        and all(ord(char) >= 32 for char in value),
        "Unsafe relative path: " + repr(value),
    )
    return value


def checked_path(path: Path, *, directory: bool = False) -> Path:
    """Reject symlinks in every existing component, including input root aliases."""
    path = path.absolute()
    require(".." not in path.parts, "Parent traversal in path")
    for item in [*reversed(path.parents), path]:
        try:
            mode = item.lstat().st_mode
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(mode), "Symlink path component: " + str(item))
        require(stat.S_ISREG(mode) or stat.S_ISDIR(mode), "Special file: " + str(item))
    if directory:
        require(path.is_dir(), "Missing input directory: " + str(path))
    return path


def digest(path: Path) -> str:
    checked_path(path)
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "Expected a regular file")
        count = 0
        while chunk := stream.read(1024 * 1024):
            count += len(chunk)
            require(count <= MAX_FILE, "File exceeds refresh bound")
            hasher.update(chunk)
    return hasher.hexdigest()


def pairs_unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in items:
        require(key not in result, "Repeated JSON key: " + key)
        result[key] = value
    return result


def read_json(path: Path) -> dict[str, Any]:
    checked_path(path)
    require(path.stat().st_size <= MAX_JSON, "JSON exceeds refresh bound")
    data = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=pairs_unique,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")),
    )
    require(isinstance(data, dict), "Expected JSON object")
    assert isinstance(data, dict)
    return data


def write_json(path: Path, value: Any) -> None:
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    require(len(raw) <= MAX_JSON, "JSON exceeds refresh bound")
    with path.open("xb") as stream:
        stream.write(raw)


def inventory(root: Path, *, limit: int = MAX_TOTAL, source_tree: bool = False) -> dict[str, str]:
    checked_path(root, directory=True)
    paths: list[Path] = []
    size = 0
    for directory, folders, files in os.walk(root, followlinks=False):
        if source_tree:
            folders[:] = [
                name
                for name in folders
                if name not in {"__pycache__", ".pytest_cache", ".ruff_cache"}
            ]
        for name in sorted(folders + files):
            path = Path(directory) / name
            checked_path(path)
            if path.is_file():
                paths.append(path)
                size += path.stat().st_size
                require(
                    len(paths) <= MAX_FILES and size <= limit,
                    "Tree exceeds refresh bound",
                )
    return {relative(p.relative_to(root).as_posix()): digest(p) for p in sorted(paths)}


def executable_sources(root: Path, *, extended: bool) -> dict[str, str]:
    result: dict[str, str] = {}
    for folder in ("models", "R", "python"):
        # Preparation excludes interpreter caches; they are never reused as source.
        for path, sha in inventory(root / folder, limit=SOURCE_LIMIT, source_tree=True).items():
            if "__pycache__" not in PurePosixPath(path).parts:
                result[folder + "/" + path] = sha
    for name in BASE_INVENTORY + (EXTRA_INVENTORY if extended else []):
        result[name] = digest(root / name)
    return dict(sorted(result.items()))


def checked_hashes(root: Path, expected: dict[str, str]) -> None:
    require(isinstance(expected, dict) and bool(expected), "Missing hash inventory")
    for name, sha in expected.items():
        relative(name)
        require(isinstance(sha, str) and SHA256.fullmatch(sha) is not None, "Invalid SHA256")
        require(digest(root / name) == sha, "Hash mismatch: " + name)


def preparer_compatible(old: str, new: str) -> bool:
    """Only the reviewed source-inventory list extension can change preparation."""
    before, after = ast.parse(old), ast.parse(new)
    matches = []
    for node in ast.walk(after):
        if (
            isinstance(node, ast.List)
            and all(isinstance(item, ast.Constant) for item in node.elts)
            and ast.literal_eval(node) == BASE_INVENTORY + EXTRA_INVENTORY
        ):
            matches.append(node)
    if len(matches) != 1:
        return False
    matches[0].elts = matches[0].elts[: len(BASE_INVENTORY)]
    return ast.dump(before, include_attributes=False) == ast.dump(after, include_attributes=False)


def source_admission(
    old: Path, current: Path, manifest: dict[str, Any], allowed: list[str]
) -> tuple[dict[str, str], dict[str, Any]]:
    recorded = manifest["source_sha256"]
    checked_hashes(old, recorded)
    require(
        executable_sources(old, extended=False) == recorded,
        "Old source inventory differs",
    )
    now = executable_sources(current, extended=True)
    require(set(now) == set(recorded) | set(EXTRA_INVENTORY), "Source inventory changed")
    require(
        digest(current / "refresh_runtime.py") == digest(Path(__file__)),
        "Executing refresh source differs from admitted source",
    )
    require(len(allowed) == len(set(allowed)), "Repeated allowed runtime path")
    for name in allowed:
        relative(name)
        require(
            name == "tests/pure.R"
            or (name in recorded and name.startswith("R/") and name != "R/compile.R")
            or (name in recorded and name.startswith("python/") and name.endswith(".py")),
            "Not an allowed runtime controller: " + name,
        )
    changes = {}
    for name, sha in now.items():
        if name == "refresh_runtime.py":
            continue
        before = recorded.get(name, digest(old / name) if name == "tests/pure.R" else None)
        if before == sha:
            continue
        if name == "prepare.py":
            require(
                preparer_compatible((old / name).read_text(), (current / name).read_text()),
                "Preparation logic changed beyond source inventory",
            )
        else:
            require(name in allowed, "Undeclared runtime or immutable build change: " + name)
        changes[name] = {"before_sha256": before, "after_sha256": sha}
    require(set(allowed) <= set(changes), "Declared runtime path did not change")
    require(
        "prepare.py" in changes,
        "Refresh requires the approved preparation inventory extension",
    )
    return now, changes


def load_preparer(source: Path) -> Any:
    spec = importlib.util.spec_from_file_location(
        "validated_reference_prepare", source / "prepare.py"
    )
    require(spec is not None and spec.loader is not None, "Cannot load validated preparer")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def description(path: Path) -> dict[str, str]:
    checked_path(path)
    require(path.stat().st_size <= 512_000, "DESCRIPTION exceeds bound")
    fields: dict[str, str] = {}
    key: str | None = None
    for line in path.read_text().splitlines():
        if line[:1].isspace():
            require(key is not None, "Orphan DESCRIPTION continuation")
            assert key is not None
            fields[key] += " " + line.strip()
        elif line:
            key, separator, value = line.partition(":")
            require(bool(separator) and key not in fields, "Invalid DESCRIPTION field")
            fields[key] = value.strip()
    return fields


def validate_prepared(
    prepared: Path, old: Path, manifest: dict[str, Any], preparer: Any
) -> tuple[dict[str, str], dict[str, str], str]:
    require(
        manifest.get("schema_version") == 1 and manifest.get("kind") == KIND,
        "Unknown manifest",
    )
    lock = read_json(old / "dependencies.lock.json")
    preparer.validate_lock(lock)
    require(manifest["r_version"] == lock["r_version"], "Locked R version differs")
    require(
        manifest["upstream_revision"] == lock["upstream"]["revision"]
        and manifest["upstream_archive_sha256"] == lock["upstream"]["sha256"]
        and manifest["upstream_license"] == lock["upstream"]["license"],
        "Upstream provenance differs",
    )
    registry = read_json(old / "registry.json")
    require(
        set(registry["models"]) == set(manifest["models"]),
        "Registered model set differs",
    )
    require(
        len(registry["models"]) == len(set(registry["models"])),
        "Repeated registered model",
    )
    compiled = read_json(prepared / "models/compile.json")
    require(
        compiled
        == {key: manifest[key] for key in ("models", "r_version", "architecture", "packages")},
        "Compile metadata differs from preparation",
    )
    for name, record in manifest["models"].items():
        require(NAME.fullmatch(name) is not None, "Unsafe model name")
        require(
            record["library"] == "models/" + name + ".so",
            "Unexpected native model path",
        )
        require(
            record["framework"] == "CppAD" and record["flags"] == "-O1 -g0",
            "Build flags differ",
        )
        checked_hashes(prepared, {record["library"]: record["sha256"]})
        checked_hashes(old, {"models/" + name + ".cpp": record["source_sha256"]})
        checked_hashes(prepared, {"models/" + name + ".cpp": record["source_sha256"]})
    require(
        set(manifest["package_files"]) == set(manifest["packages"]),
        "Package hash set differs",
    )
    for name, files in manifest["package_files"].items():
        require(NAME.fullmatch(name) is not None, "Unsafe package name")
        checked_hashes(prepared / "library" / name, files)
    expected_packages = {item["name"]: item["version"] for item in lock["packages"]}
    expected_packages[lock["upstream"]["name"]] = lock["upstream"]["version"]
    library_names = {path.name for path in (prepared / "library").iterdir()}
    require(
        library_names == set(expected_packages),
        "Installed package set differs from lock",
    )
    platforms = set()
    for name, expected in expected_packages.items():
        require(NAME.fullmatch(name) is not None, "Unsafe installed package name")
        fields = description(prepared / "library" / name / "DESCRIPTION")
        require(
            fields.get("Package") == name and fields.get("Version") == expected,
            "Installed package identity differs: " + name,
        )
        built = [item.strip() for item in fields.get("Built", "").split(";")]
        require(
            len(built) >= 2 and built[0] == "R " + manifest["r_version"],
            "Installed package R version differs",
        )
        # R records an empty platform for packages without native code.
        if built[1]:
            platforms.add(built[1])
        if name in manifest["packages"]:
            require(
                expected.replace("-", ".") == manifest["packages"][name],
                "Compiled package version differs",
            )
    require(len(platforms) == 1, "Missing or conflicting installed native platform")
    platform = platforms.pop()
    require(
        platform.startswith(manifest["architecture"] + "-"),
        "Installed architecture differs",
    )
    sources = {}
    for entry in lock["packages"]:
        name = entry["name"] + "_" + entry["version"] + ".tar.gz"
        sources[name] = entry["sha256"]
        checked_hashes(prepared / "sources", {name: entry["sha256"]})
        preparer.verify_archive_metadata(prepared / "sources" / name, entry)
    sources["glmmTMB-pinned.tar.gz"] = lock["upstream"]["sha256"]
    checked_hashes(prepared / "sources", {"glmmTMB-pinned.tar.gz": lock["upstream"]["sha256"]})
    with tarfile.open(prepared / "sources/glmmTMB-pinned.tar.gz") as archive:
        expected_name = lock["upstream"]["package_prefix"] + "DESCRIPTION"
        members = [member for member in archive.getmembers() if member.name == expected_name]
        require(
            len(members) == 1 and members[0].isfile() and 0 < members[0].size <= 512_000,
            "Upstream DESCRIPTION missing or unsafe",
        )
        stream = archive.extractfile(members[0])
        require(stream is not None, "Upstream DESCRIPTION unavailable")
        assert stream is not None
        lines = stream.read(512_001).decode().splitlines()
        for field, value in (
            ("Package", "glmmTMB"),
            ("Version", lock["upstream"]["version"]),
        ):
            require(
                [line.partition(":")[2].strip() for line in lines if line.startswith(field + ":")]
                == [value],
                "Upstream DESCRIPTION identity differs",
            )
    checked_hashes(prepared / "sources", sources)
    require(
        set(inventory(prepared / "sources")) == set(sources),
        "Retained archive set differs",
    )
    return expected_packages, sources, platform


def copy_checked(
    source: Path,
    destination: Path,
    expected: dict[str, str],
    *,
    source_tree: bool = False,
) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for name, sha in expected.items():
        relative(name)
        before = source / name
        checked_path(before)
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        mode = before.stat().st_mode
        with before.open("rb") as reader, target.open("xb") as writer:
            hasher = hashlib.sha256()
            count = 0
            while chunk := reader.read(1024 * 1024):
                count += len(chunk)
                require(count <= MAX_FILE, "Copied file exceeds refresh bound")
                writer.write(chunk)
                hasher.update(chunk)
        require(
            hasher.hexdigest() == sha and digest(target) == sha,
            "File changed during copy: " + name,
        )
        target.chmod(stat.S_IMODE(mode) & 0o777)
    require(
        inventory(source, source_tree=source_tree) == expected,
        "Source tree changed during copy",
    )
    require(
        inventory(destination, source_tree=source_tree) == expected,
        "Copied tree differs",
    )


def run_bounded(command: list[str], log: Path, environment: dict[str, str], timeout: int) -> None:
    """Kill only this owned process group on deadline or excessive output."""
    with log.open("xb") as stream:
        process = subprocess.Popen(
            command,
            stdout=stream,
            stderr=subprocess.STDOUT,
            env=environment,
            start_new_session=True,
            cwd=log.parent,
            preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_LOG, MAX_LOG)),
        )
        deadline = time.monotonic() + timeout
        try:
            while process.poll() is None:
                require(time.monotonic() < deadline, "Refresh subprocess exceeded deadline")
                require(
                    log.stat().st_size < MAX_LOG,
                    "Refresh subprocess exceeded log bound",
                )
                time.sleep(0.05)
            require(log.stat().st_size < MAX_LOG, "Refresh subprocess exceeded log bound")
            require(process.returncode == 0, "Refresh check failed; see " + log.name)
        except BaseException:
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise


R_IDENTITY = """args <- commandArgs(TRUE)
lib <- normalizePath(args[1], mustWork=TRUE)
names <- readLines(args[2], warn=FALSE)
paths <- setNames(lapply(names, function(n) normalizePath(find.package(n), mustWork=TRUE)), names)
versions <- setNames(lapply(names, function(n) as.character(utils::packageVersion(n))), names)
stopifnot(all(vapply(names, function(n) identical(paths[[n]], file.path(lib,n)), logical(1))))
cat(jsonlite::toJSON(list(r_version=as.character(getRversion()), architecture=R.version$arch,
  platform=R.version$platform, dynlib_ext=.Platform$dynlib.ext,
  packages=versions), auto_unbox=TRUE))
"""
R_PARSE = """args <- commandArgs(TRUE)
for (path in readLines(args[1], warn=FALSE)) invisible(parse(file=path, keep.source=TRUE))
cat("All admitted R sources parsed without evaluation\\n")
"""


def checks(
    output: Path, packages: dict[str, str], manifest: dict[str, Any], platform: str
) -> dict[str, Any]:
    source, library, logs = output / "source", output / "library", output / "logs"
    private = output / "check-home"
    private.mkdir()
    environment = {
        name: value
        for name, value in os.environ.items()
        if not name.startswith(("R_", "LD_PRELOAD", "DYLD_"))
    }
    environment.update(
        HOME=str(private),
        TMPDIR=str(private),
        R_LIBS_USER=str(library),
        R_LIBS_SITE=str(library),
        MAKEFLAGS="-j1",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
    )
    names = logs / "packages.txt"
    names.write_text("\n".join(sorted(packages)) + "\n")
    run_bounded(
        ["Rscript", "--vanilla", "-e", R_IDENTITY, str(library), str(names)],
        logs / "identity.json",
        environment,
        60,
    )
    identity = read_json(logs / "identity.json")
    require(
        identity
        == {
            "r_version": manifest["r_version"],
            "architecture": manifest["architecture"],
            "platform": platform,
            "dynlib_ext": ".so",
            "packages": {name: value.replace("-", ".") for name, value in packages.items()},
        },
        "Current R, native platform or package resolution differs",
    )
    r_paths = sorted(str(path) for path in (source / "R").rglob("*.R")) + [
        str(source / "tests/pure.R")
    ]
    (logs / "r-sources.txt").write_text("\n".join(r_paths) + "\n")
    for path in [
        source / "prepare.py",
        source / "refresh_runtime.py",
        *(source / "python").rglob("*.py"),
    ]:
        ast.parse(path.read_text(), filename=str(path))
    run_bounded(
        ["Rscript", "--vanilla", "-e", R_PARSE, str(logs / "r-sources.txt")],
        logs / "parse.log",
        environment,
        60,
    )
    run_bounded(
        ["Rscript", "--vanilla", str(source / "tests/pure.R"), str(source)],
        logs / "pure.log",
        environment,
        180,
    )
    return identity


def space_admission(output: Path, trees: list[tuple[Path, dict[str, str]]]) -> dict[str, int]:
    """Refuse known insufficient destination space before creating a partial tree."""
    parent = output.parent
    while not parent.exists():
        parent = parent.parent
    checked_path(parent, directory=True)
    block = max(4096, os.statvfs(parent).f_frsize)
    # Account for allocated blocks, file metadata, provenance and bounded logs.
    estimated = sum(
        ((root / name).stat().st_size + block - 1) // block * block + block
        for root, hashes in trees
        for name in hashes
    )
    require(estimated <= MAX_TOTAL, "Combined refresh artifacts exceed the byte bound")
    reserve = 64 * 1024 * 1024
    required = estimated + reserve
    available = shutil.disk_usage(parent).free
    require(available >= required, "Insufficient free space for a fresh runtime refresh")
    return {
        "available_bytes": available,
        "required_bytes": required,
        "estimated_file_bytes": estimated,
        "reserve_bytes": reserve,
        "allocation_block_bytes": block,
    }


def refresh(
    prepared: Path,
    old_source: Path,
    source: Path,
    output: Path,
    expected_manifest_sha256: str,
    allowed: list[str],
) -> dict[str, Any]:
    require(
        SHA256.fullmatch(expected_manifest_sha256) is not None,
        "Require expected manifest SHA256",
    )
    prepared, old_source, source = [
        checked_path(p, directory=True) for p in (prepared, old_source, source)
    ]
    output = checked_path(output)
    require(not output.exists(), "Use a fresh output directory")
    for parent in (prepared, old_source, source):
        require(
            not output.is_relative_to(parent) and not parent.is_relative_to(output),
            "Output overlaps input",
        )
    manifest_path = prepared / "manifest.json"
    require(digest(manifest_path) == expected_manifest_sha256, "Old manifest SHA256 differs")
    manifest = read_json(manifest_path)
    require(
        manifest.get("schema_version") == 1 and manifest.get("kind") == KIND,
        "Unknown manifest",
    )
    now, changes = source_admission(old_source, source, manifest, allowed)
    preparer = load_preparer(source)
    packages, archives, platform = validate_prepared(prepared, old_source, manifest, preparer)
    # Record every reused byte, distinguishing these observations from old signed-off hashes.
    reused = {name: inventory(prepared / name) for name in ("library", "models", "sources")}
    current_files = inventory(source, limit=SOURCE_LIMIT, source_tree=True)
    old_files = inventory(old_source, limit=SOURCE_LIMIT, source_tree=True)
    space = space_admission(
        output,
        [(prepared / name, hashes) for name, hashes in reused.items()] + [(source, current_files)],
    )
    output.mkdir(parents=True, exist_ok=False)
    (output / "logs").mkdir()
    try:
        for name, hashes in reused.items():
            copy_checked(prepared / name, output / name, hashes)
        copy_checked(source, output / "source", current_files, source_tree=True)
        identity = checks(output, packages, manifest, platform)
        # Pure checks and copying must not alter either inputs or copied immutable artifacts.
        require(
            inventory(source, limit=SOURCE_LIMIT, source_tree=True) == current_files,
            "Current source changed during refresh",
        )
        require(
            inventory(old_source, limit=SOURCE_LIMIT, source_tree=True) == old_files,
            "Old source changed during refresh",
        )
        for name, hashes in reused.items():
            require(
                inventory(prepared / name) == hashes and inventory(output / name) == hashes,
                "Artifact changed during checks: " + name,
            )
        require(
            inventory(output / "source", limit=SOURCE_LIMIT, source_tree=True) == current_files,
            "Source snapshot changed during checks",
        )
        require(
            digest(manifest_path) == expected_manifest_sha256,
            "Old manifest changed during refresh",
        )
        provenance = output / "provenance"
        provenance.mkdir()
        (provenance / "old-manifest.json").write_bytes(manifest_path.read_bytes())
        require(
            digest(provenance / "old-manifest.json") == expected_manifest_sha256,
            "Provenance manifest differs",
        )
        all_hashes = {
            group + "/" + name: sha
            for group, hashes in reused.items()
            for name, sha in hashes.items()
        }
        write_json(provenance / "reused-files.json", all_hashes)
        write_json(provenance / "old-source-observed.json", old_files)
        write_json(provenance / "current-source.json", current_files)
        for name in ("NOTICE.md", "LICENSE"):
            original = source / name
            require(original.is_file(), "Missing source license/notice")
            (output / name).write_bytes(original.read_bytes())
        updated = copy.deepcopy(manifest)
        updated.update(
            source_sha256=now,
            scope=(
                "dependency/template reuse and runtime-source checks only; "
                "numerical acceptance not run"
            ),
            refresh={
                "schema_version": 1,
                "kind": "runtime-source-refresh",
                "old_manifest_sha256": expected_manifest_sha256,
                "old_manifest_path": "provenance/old-manifest.json",
                "runtime_changes": changes,
                "new_inventory_paths": EXTRA_INVENTORY,
                "reused_files_sha256": digest(provenance / "reused-files.json"),
                "reused_files_path": "provenance/reused-files.json",
                "current_source_inventory_sha256": digest(provenance / "current-source.json"),
                "old_source_observed_sha256": digest(provenance / "old-source-observed.json"),
                "recorded_old_hashes_verified": True,
                "additional_reused_hashes_observed_now": True,
                "archives_verified": archives,
                "runtime_identity": identity,
                "checks": {
                    "r_parse": "passed",
                    "python_parse": "passed",
                    "pure": "passed",
                },
                "check_files_sha256": inventory(output / "logs"),
                "numerical_acceptance": "not_run",
                "installed_or_compiled": False,
                "destination_space_admission": space,
            },
        )
        write_json(output / ".manifest.pending.json", updated)
        (output / ".manifest.pending.json").rename(output / "manifest.json")
    except BaseException as error:
        # Do not publish a successful manifest on a partial refresh. Retain owned diagnostics.
        with suppress(OSError):
            write_json(
                output / "failure.json",
                {
                    "status": "failed",
                    "error_type": type(error).__name__,
                    "message": str(error)[:2000],
                },
            )
        raise
    return {
        "prepared": str(output),
        "source": str(output / "source"),
        "manifest_sha256": digest(output / "manifest.json"),
        "numerical_acceptance": "not_run",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("prepared", "old-source", "source", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--allow-runtime-change", action="append", default=[])
    args = parser.parse_args()
    print(
        json.dumps(
            refresh(
                args.prepared,
                args.old_source,
                args.source,
                args.output,
                args.expected_manifest_sha256,
                args.allow_runtime_change,
            )
        )
    )


if __name__ == "__main__":
    main()
