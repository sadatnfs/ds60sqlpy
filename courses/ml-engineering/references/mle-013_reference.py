"""mle-013: local, bounded ML engineering investigation."""

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


def example_two():
    ledger = {}
    old = execute_pipeline(ledger, [1, 2, 3])
    new = execute_pipeline(ledger, [1, 2, 4])
    assert old != new and ledger["model"]["mean"] == 14 / 3
    assert ledger["features"] == [2, 4, 8]
    return {"changed_input_invalidates_reuse": True, "new_mean": ledger["model"]["mean"]}


def main():
    print(example_one())
    print(example_two())
    print("mle-013 reference checks passed")


if __name__ == "__main__":
    main()
