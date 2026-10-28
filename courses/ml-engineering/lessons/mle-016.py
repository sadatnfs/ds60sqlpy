"""mle-016: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: List the checks that must precede pointer replacement.
# TODO 2: Keep the rejected candidate and its diagnostic in an owned review area.
# TODO 3: Describe a timeout after activation may have completed.
# TODO 4: Explain why rolling back only coefficients may be insufficient.
# TODO 5: State what os.replace does not establish.
# TODO 6: Use the local-system CLI to activate v2 and return to v1.
