"""mle-013: worked starting point; complete the guide's six changes."""

import contextlib
import hashlib
import json


def digest(data):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def execute_pipeline(ledger, events, fail_after_features=False):
    source_id = digest(events)
    if ledger.get("source_id") != source_id:
        ledger.clear()
        ledger["source_id"] = source_id
    if "features" not in ledger:
        ledger["features"] = [2 * x for x in events]
    if fail_after_features:
        raise RuntimeError("deliberate interruption after checkpoint")
    if "model" not in ledger:
        ledger["model"] = {"mean": sum(ledger["features"]) / len(ledger["features"])}
    if "publication" not in ledger:
        ledger["publication"] = digest(ledger["model"])
    return ledger["publication"]


def example_one():
    ledger = {}
    with contextlib.suppress(RuntimeError):
        execute_pipeline(ledger, [1, 2, 3], True)
    assert "features" in ledger and "publication" not in ledger
    first = execute_pipeline(ledger, [1, 2, 3])
    second = execute_pipeline(ledger, [1, 2, 3])
    assert first == second and ledger["model"]["mean"] == 4
    return {"checkpoint_retained": True, "idempotent_publication": first, "mean": 4}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Identify which stage creates the consumer-facing result.
# TODO 2: Describe a timeout after publication may already have occurred.
# TODO 3: Include transformation-code identity with the input identity.
# TODO 4: Change a feature transformation and identify affected stages.
# TODO 5: Retain the interruption reason and completed stages.
# TODO 6: State what framework execution must still qualify.
