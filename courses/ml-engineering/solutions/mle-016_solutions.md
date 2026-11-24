# mle-016: explained reference

Activate and recover model state through explicit accepted versions.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Validate before switching

The service project also validates feature order, finite coefficients and positive scales. Broader model acceptance still needs its evaluation and operational evidence.

activate() computes sha256 of the written candidate and compares it with expected_hash before writing current.pending. In example_one the hash "0" * 64 cannot match {"weight": 99.0}, so ValueError fires and current.json stays byte-identical to the v1 pointer. Writing the pointer first and validating afterwards would expose consumers to v2 during the gap.

**Expected:** They include artifact identity and compatible structure.

## 2. Retain failed evidence

Do not overwrite the previous accepted version or erase the failure merely to simplify directory contents. Apply an explicit retention policy later.

Note that the fixture leaves v2.json on disk after the hash mismatch, because the candidate is written before it is checked. That file is the evidence: record its hash and the ValueError message beside it so a reviewer can see why it was rejected.

**Expected:** The failure remains explainable.

## 3. Reconcile an unknown response

Use the intended version/hash to reconcile actual state. Blindly repeating activation can create misleading audit history in a larger system.

Read current.json and compare its version and sha256 with the intended values. If they already match, the activation completed and the client's timeout lost only the response. Repeating activate() would rewrite the same pointer and add a second audit entry for one change.

**Expected:** The next action reads the pointer before retrying.

## 4. Check bundle compatibility

Restore a compatible model and feature transformation bundle. A file-level rollback can be technically successful while predictions are semantically wrong.

In this fixture the model is a single weight, so the pointer is the whole story. A real bundle also fixes feature order and scaling; restoring v1 coefficients beside a v2 scaler would load cleanly and produce wrong scores.

**Expected:** The feature/preprocessing contract must also match.

## 5. Separate local and distributed claims

Use suitable synchronization, persistence and recovery mechanisms for the deployed environment, and test partial failures explicitly.

temporary.replace() maps to os.replace, which is atomic for readers on one local filesystem. It does not fsync the directory, so a power loss could still lose the new pointer, and it coordinates nothing between replicas reading different disks.

**Expected:** It does not prove multi-replica consensus or power-loss durability.

## 6. Exercise the real project

Retain its ownership marker and state. The checker verifies real HTTP, model integrity and replacement without retraining, while leaving external production claims out of scope.

Example_two runs v1, v2, v1 and confirms current.json says v1 with no current.pending left. For the real project, check that HTTP responses report the version and that the v1 hash after rollback equals the original v1 hash.

**Expected:** Actual HTTP predictions identify the selected version and restore exactly.

## Complete reference

```python
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
```

## Interpretation

Test failure before publication and exact rollback behavior, then distinguish local atomicity from the additional guarantees required by a deployed multi-process system.
