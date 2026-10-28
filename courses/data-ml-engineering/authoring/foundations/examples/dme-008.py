"""Actual content identities for a bounded reproducible computation bundle."""

import hashlib
import json
import platform
import runpy
import tempfile
from pathlib import Path


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(root, paths):
    return {name: fingerprint(root / name) for name in sorted(paths)}


def verify(root, recorded):
    changed = [
        name
        for name, digest in recorded.items()
        if not (root / name).is_file() or fingerprint(root / name) != digest
    ]
    if changed:
        raise ValueError("Recorded inputs changed: " + ", ".join(changed))


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "input.json").write_text("[2, 3, 1]\n", "utf-8")
        (root / "transform.py").write_text(
            "def compute(values):\n    return sum(values)\n", "utf-8"
        )
        (root / "configuration.json").write_text('{"unit": "packages"}\n', "utf-8")
        (root / "environment.json").write_text(
            json.dumps(
                {
                    "python": platform.python_version(),
                    "implementation": platform.python_implementation(),
                    "system": platform.system(),
                },
                sort_keys=True,
            )
            + "\n",
            "utf-8",
        )
        names = ["input.json", "transform.py", "configuration.json", "environment.json"]
        recorded = manifest(root, names)
        assert recorded == manifest(root, list(reversed(names)))
        verify(root, recorded)
        namespace = runpy.run_path(str(root / "transform.py"))
        result = namespace["compute"](json.loads((root / "input.json").read_text("utf-8")))
        assert result == 6
        return {
            "result": result,
            "input_identity": recorded["input.json"],
            "recorded_files": sorted(recorded),
            "verified": True,
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "input.json").write_text("[2, 3, 1]\n", "utf-8")
        recorded = manifest(root, ["input.json"])
        (root / "input.json").write_text("[2, 3, 4]\n", "utf-8")
        try:
            verify(root, recorded)
        except ValueError:
            rejected = True
        else:
            raise AssertionError("An old result cannot qualify changed input bytes")
        new = manifest(root, ["input.json"])
        assert new != recorded
        assert sum(json.loads((root / "input.json").read_text("utf-8"))) == 9
        (root / "input.json").write_text("[2,3,4]\n", "utf-8")
        reformatted = manifest(root, ["input.json"])
        assert reformatted != new
        assert sum(json.loads((root / "input.json").read_text("utf-8"))) == 9
        return {
            "old_claim_rejected": rejected,
            "new_result": 9,
            "identity_changed": True,
            "hash_is_not_source_authentication": True,
            "same_values_can_have_different_byte_identities": True,
        }


def main():
    print("A reviewable local computation bundle:", example_one())
    print("Changed data invalidates the old result:", example_two())


if __name__ == "__main__":
    main()
