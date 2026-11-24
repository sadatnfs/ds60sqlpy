# mle-013: explained reference

Define checkpoint and retry behavior using artifact identities.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Name the side effect

Describe whether each stage is pure, idempotent or requires reconciliation. A successful earlier stage does not authorize all later effects.

In execute_pipeline the publication key holds digest(ledger["model"]); it is the only value a consumer reads. features and model are pure functions of events, so recomputing them is harmless, but publishing twice to a real destination would not be.

**Expected:** Publication is separate from feature and model computation.

## 2. Add an uncertain outcome

Read the publication record or artifact and determine whether the operation completed. Do not blindly repeat a non-idempotent effect.

Suppose the step after ledger["publication"] is assigned times out. Compare the stored publication with digest(ledger["model"]); if they match, the effect already happened and repeating it is unnecessary. Retrying unconditionally would be safe in this dictionary but could send a second notification in a real system.

**Expected:** The response checks the intended identity before repeating.

## 3. Version the code

Record the source or transformation version that produced a checkpoint. Reusing it under different logic can silently return stale results.

Change the transformation to 3 * x but keep events [1, 2, 3]. source_id is unchanged, so the ledger keeps features [2, 4, 6] and mean 4: a stale result with no error. Including a transform version in the digested identity, for example digest({"events": events, "transform": "double-v1"}), forces recomputation. Verify the new mean is 6.

**Expected:** Changed logic invalidates incompatible reuse.

## 4. Invalidate a descendant

Recompute the affected descendants or use a proven compatible reuse rule. A checkpoint is useful only with its dependencies.

Example_two shows the input case: [1, 2, 4] clears the whole ledger and yields features [2, 4, 8] and mean 14/3. Deleting only ledger["features"] after a code change would recompute features but keep the old model and publication, because those keys remain present.

**Expected:** Model, evaluation and publication need new evidence.

## 5. Keep failure evidence

Record stage identities and actual outcomes. Avoid overwriting the original failure with a later success without preserving the distinction.

After the deliberate interruption the ledger holds only source_id and features, with no record that a failure occurred. Add an attempts list with the RuntimeError text. Note that ledger.clear() on a source change would erase it too, so keep attempts outside the cleared dictionary.

**Expected:** The next attempt can explain what was reused.

## 6. Choose a real orchestrator

Use the existing Prefect route or an explicitly prepared external project to test actual orchestration. Do not call this dictionary a deployed scheduler.

The ledger here lives in memory and vanishes when the process ends, so it cannot survive a worker restart. A real orchestrator must show that the features checkpoint persists across processes and that a retry of publication is detected as already done.

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

Demonstrate a known interruption and an input change, then map those contracts to a real orchestrator with separate persistence and execution evidence.
