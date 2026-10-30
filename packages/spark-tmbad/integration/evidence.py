"""Collect bounded tmpfs evidence through the running container namespace."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import unicodedata
from pathlib import Path, PurePosixPath

MAX_FILES = 128
MAX_FILE = 8 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024


def export_payload(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Evidence root is not an ordinary directory")
    records = []
    total = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Evidence must not contain symbolic links")
        if path.is_dir():
            continue
        if not path.is_file() or path.stat().st_size > MAX_FILE:
            raise ValueError("Evidence member is not a bounded ordinary file")
        raw = path.read_bytes()
        total += len(raw)
        if len(raw) > MAX_FILE or total > MAX_TOTAL or len(records) >= MAX_FILES:
            raise ValueError("Evidence export exceeded its byte or file bound")
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "base64": base64.b64encode(raw).decode("ascii"),
            }
        )
    return {"schema_version": 1, "files": records}


def retain_payload(payload, destination):
    if set(payload) != {"schema_version", "files"} or payload["schema_version"] != 1:
        raise ValueError("Unknown evidence export schema")
    files = payload["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise ValueError("Invalid evidence file count")
    seen = set()
    staged = []
    total = 0
    for row in files:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256", "base64"}:
            raise ValueError("Invalid evidence record")
        name = row["path"]
        if not isinstance(name, str):
            raise ValueError("Evidence name must be text")
        path = PurePosixPath(name)
        folded = unicodedata.normalize("NFC", name).casefold()
        if (
            not name
            or not path.parts
            or len(path.parts) > 16
            or path.is_absolute()
            or ".." in path.parts
            or str(path) != name
            or "\\" in name
            or "\0" in name
            or folded in seen
        ):
            raise ValueError("Unsafe or colliding evidence name")
        seen.add(folded)
        if type(row["bytes"]) is not int or not 0 <= row["bytes"] <= MAX_FILE:
            raise ValueError("Invalid evidence byte count")
        raw = base64.b64decode(row["base64"], validate=True)
        total += len(raw)
        if (
            len(raw) != row["bytes"]
            or total > MAX_TOTAL
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
        ):
            raise ValueError("Evidence byte/hash binding differs")
        target = destination / path
        if any(parent.is_symlink() for parent in (target, *target.parents)):
            raise ValueError("Evidence destination must not contain links")
        if target.exists() and (not target.is_file() or target.read_bytes() != raw):
            raise ValueError("Preserve different retained evidence")
        staged.append((target, raw))
    for target, raw in staged:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            with target.open("xb") as stream:
                stream.write(raw)
    return len(staged)


def collect_driver_evidence(identifier, destination, environment, *, required):
    result = subprocess.run(
        ["docker", "exec", identifier, "python3", "/integration/evidence.py"],
        env=environment,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if result.returncode:
        if required:
            raise RuntimeError("Running driver evidence export failed")
        return False
    if len(result.stdout) > 24 * 1024 * 1024:
        raise ValueError("Evidence envelope exceeded its bound")
    payload = json.loads(result.stdout)
    retain_payload(payload, destination)
    if required and not (destination / "driver.json").is_file():
        raise RuntimeError("Driver did not produce its final qualification record")
    return True


if __name__ == "__main__":
    print(json.dumps(export_payload(Path("/work/evidence")), separators=(",", ":")))
