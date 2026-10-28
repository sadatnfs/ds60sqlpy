"""mle-016: local, bounded ML engineering investigation."""

import contextlib
import hashlib
import json
import tempfile
from pathlib import Path


def activate(root, version, model, expected_hash):
    candidate = root / (version + ".json")
    candidate.write_text(json.dumps(model, sort_keys=True))
    actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if actual != expected_hash:
        raise ValueError("candidate hash mismatch")
    temporary = root / "current.pending"
    temporary.write_text(json.dumps({"version": version, "sha256": actual}))
    temporary.replace(root / "current.json")


def example_one():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        model = {"weight": 2.0}
        encoded = json.dumps(model, sort_keys=True).encode()
        expected = hashlib.sha256(encoded).hexdigest()
        activate(root, "v1", model, expected)
        before = (root / "current.json").read_bytes()
        with contextlib.suppress(ValueError):
            activate(root, "v2", {"weight": 99.0}, "0" * 64)
        assert (root / "current.json").read_bytes() == before
        return {"failed_candidate_kept_active_v1": True}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for version, weight in [("v1", 2.0), ("v2", 3.0), ("v1", 2.0)]:
            model = {"weight": weight}
            encoded = json.dumps(model, sort_keys=True).encode()
            activate(root, version, model, hashlib.sha256(encoded).hexdigest())
        assert json.loads((root / "current.json").read_text())["version"] == "v1"
        assert not (root / "current.pending").exists()
        return {"deliberate_pointer_rollback": True, "accepted_version": "v1"}


def main():
    print(example_one())
    print(example_two())
    print("mle-016 reference checks passed")


if __name__ == "__main__":
    main()
