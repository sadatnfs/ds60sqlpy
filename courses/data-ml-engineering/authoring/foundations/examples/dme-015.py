"""Actual local atomic pointer publication under one declared publisher."""

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def bounded(path):
    with path.open("rb") as stream:
        value = stream.read(4097)
    if len(value) > 4096:
        raise ValueError("Artifact exceeds this bounded example")
    return value


def version_directory(root, version):
    if not isinstance(version, str) or re.fullmatch(r"v[1-9][0-9]*", version) is None:
        raise ValueError("Invalid version identity")
    return root / "versions" / version


def prepare_version(root, version, values):
    if (
        not isinstance(values, list)
        or len(values) > 100
        or any(type(value) is not int or not 1 <= value <= 1_000_000 for value in values)
    ):
        raise ValueError("Use a bounded list of positive integer package counts")
    directory = version_directory(root, version)
    directory.mkdir(parents=True, exist_ok=False)
    data = json.dumps(values, allow_nan=False).encode()
    (directory / "data.json").write_bytes(data)
    manifest = {
        "version": version,
        "rows": len(values),
        "data_sha256": hashlib.sha256(data).hexdigest(),
    }
    (directory / "manifest.json").write_text(json.dumps(manifest, sort_keys=True), "utf-8")


def read_version(root, version):
    directory = version_directory(root, version)
    raw_manifest = bounded(directory / "manifest.json")
    manifest = json.loads(raw_manifest)
    if (
        not isinstance(manifest, dict)
        or set(manifest) != {"version", "rows", "data_sha256"}
        or manifest["version"] != version
        or type(manifest["rows"]) is not int
        or not 0 <= manifest["rows"] <= 100
    ):
        raise ValueError("Manifest contract mismatch")
    data = bounded(directory / "data.json")
    if hashlib.sha256(data).hexdigest() != manifest["data_sha256"]:
        raise ValueError("Content digest differs from the recorded version")
    values = json.loads(data)
    if (
        not isinstance(values, list)
        or len(values) != manifest["rows"]
        or any(type(value) is not int or not 1 <= value <= 1_000_000 for value in values)
    ):
        raise ValueError("Data schema or row count differs")
    return values, raw_manifest


def activate(root, version):
    _, raw_manifest = read_version(root, version)
    pointer = {"version": version, "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest()}
    pending = root / "current.pending"
    pending.write_text(json.dumps(pointer, sort_keys=True), "utf-8")
    pending.replace(root / "current.json")


def current(root):
    pointer = json.loads(bounded(root / "current.json"))
    if not isinstance(pointer, dict) or set(pointer) != {"version", "manifest_sha256"}:
        raise ValueError("Pointer contract mismatch")
    values, raw_manifest = read_version(root, pointer["version"])
    if hashlib.sha256(raw_manifest).hexdigest() != pointer["manifest_sha256"]:
        raise ValueError("Manifest identity differs from the accepted pointer")
    return {"version": pointer["version"], "rows": len(values), "packages": sum(values)}


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        prepare_version(root, "v1", [2, 3, 1])
        activate(root, "v1")
        child = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import pathlib,runpy,sys; "
                    "namespace=runpy.run_path(sys.argv[1]); "
                    "namespace['prepare_version'](pathlib.Path(sys.argv[2]),"
                    "'v2',[2,3,4]); sys.exit(7)"
                ),
                str(Path(__file__).resolve()),
                str(root),
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert child.returncode == 7
        before = current(root)
        assert before == {"version": "v1", "rows": 3, "packages": 6}
        activate(root, "v2")
        after = current(root)
        assert after == {"version": "v2", "rows": 3, "packages": 9}
        return {
            "actual_child_exit": child.returncode,
            "before_activation": before,
            "after_activation": after,
            "scope": (
                "one local publisher; this is not a power-loss durability or distributed CAS test"
            ),
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        prepare_version(root, "v1", [2, 3, 1])
        activate(root, "v1")
        accepted_pointer = (root / "current.json").read_bytes()
        prepare_version(root, "v2", [2, 3, 4])
        candidate = version_directory(root, "v2") / "data.json"
        candidate.write_bytes(candidate.read_bytes() + b" ")
        try:
            activate(root, "v2")
        except ValueError:
            rejected = True
        else:
            raise AssertionError("Corrupted candidate must not become active")
        assert (root / "current.json").read_bytes() == accepted_pointer
        assert current(root)["packages"] == 6
        active = version_directory(root, "v1") / "data.json"
        active.write_bytes(active.read_bytes() + b" ")
        try:
            current(root)
        except ValueError:
            consumer_rejected = True
        else:
            raise AssertionError("A reader must not silently accept changed active bytes")
        return {
            "candidate_rejected": rejected,
            "old_pointer_preserved": True,
            "active_corruption_detected": consumer_rejected,
        }


def main():
    print("A real process failure before the publication boundary:", example_one())
    print("Integrity checks protect activation and consumption:", example_two())


if __name__ == "__main__":
    main()
