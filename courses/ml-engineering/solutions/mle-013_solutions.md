# mle-013: explained reference

Define checkpoint and retry behavior using artifact identities.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Name the side effect

Describe whether each stage is pure, idempotent or requires reconciliation. A successful earlier stage does not authorize all later effects.

**Expected:** Publication is separate from feature and model computation.

## 2. Add an uncertain outcome

Read the publication record or artifact and determine whether the operation completed. Do not blindly repeat a non-idempotent effect.

**Expected:** The response checks the intended identity before repeating.

## 3. Version the code

Record the source or transformation version that produced a checkpoint. Reusing it under different logic can silently return stale results.

**Expected:** Changed logic invalidates incompatible reuse.

## 4. Invalidate a descendant

Recompute the affected descendants or use a proven compatible reuse rule. A checkpoint is useful only with its dependencies.

**Expected:** Model, evaluation and publication need new evidence.

## 5. Keep failure evidence

Record stage identities and actual outcomes. Avoid overwriting the original failure with a later success without preserving the distinction.

**Expected:** The next attempt can explain what was reused.

## 6. Choose a real orchestrator

Use the existing Prefect route or an explicitly prepared external project to test actual orchestration. Do not call this dictionary a deployed scheduler.

**Expected:** It includes persistence, scheduling, retries and resource behavior.

## Complete reference

```python
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
```

## Interpretation

Define checkpoint and retry behavior using artifact identities. Demonstrate a known interruption and an input change, then map those contracts to a real orchestrator with separate persistence and execution evidence.
