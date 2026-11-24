# mle-001: explained reference

Define an ML product through its decision, information boundary and accepted artifacts.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Name the population

State the unit, eligibility and time boundary. A change from repeat customers to unseen customers changes the learning problem.

In this fixture the 120 rows are not 120 people: customer_id is id modulo 12, so each of 12 synthetic customers contributes exactly 10 decisions, one per cutoff from 100 to 219. Calling the population "customers" would overstate independence; a split that puts one customer's rows on both sides of train and evaluation measures memory of that customer. Verify by printing frame.groupby("customer_id").size(), which shows 10 for every customer.

**Expected:** The answer identifies synthetic customer decisions.

## 2. Exclude the target

Validate a reviewed allowlist, not every non-null column. Other leakage fields such as future status or post-decision aggregates need the same review.

The allowlist is correct here because REVIEWED_FEATURES names the three columns a reviewer approved, so a new column such as label_available_at fails even though it is numeric and complete. Selecting every column except label looks equivalent today but would silently admit cutoff, available_at and label_available_at, the last of which encodes when the answer arrives. Run the snippet: the first call returns None and the second raises ValueError mentioning label.

```python
REVIEWED_FEATURES = {"usage", "tickets", "region"}


def validate_features(contract):
    columns = set(contract["feature_columns"])
    if contract["label"] in columns:
        raise ValueError("The label cannot be a training input.")
    if not columns <= REVIEWED_FEATURES:
        raise ValueError(f"Unreviewed feature columns: {sorted(columns - REVIEWED_FEATURES)}")


validate_features({"feature_columns": ["usage", "tickets", "region"], "label": "label"})
try:
    validate_features({"feature_columns": ["usage", "label"], "label": "label"})
except ValueError as error:
    assert "label" in str(error)
else:
    raise AssertionError("The label was accepted as a feature.")
```

**Expected:** The target cannot enter training inputs accidentally.

## 3. Change the horizon

Update the label construction and availability contract, then revalidate training/evaluation cohorts. A title change alone does not implement a new target.

Concretely, label_available_at is cutoff + 4 in dataset(); a 24 hour horizon means cutoff + 24, and contract["label_horizon_hours"] must change with it. Editing only the dictionary value leaves the assertion label_available_at > cutoff passing, which is why that check alone cannot catch a horizon mismatch. Verify the new rule by checking (frame.label_available_at - frame.cutoff).unique() equals [24] after rebuilding.

**Expected:** Labels, maturity rules and evaluation need review.

## 4. Add a dependency

Add a reviewed node and prerequisite. Do not mark it complete merely because training produced a file.

Add "model_card": {"evaluate"} and change publish to {"evaluate", "model_card"}. With completed still {validate, features, train}, ready stays ["evaluate"]; after adding evaluate to completed, ready becomes ["model_card"] and publish is still absent. Making publish depend only on model_card would also block it, but would hide the evaluation edge if someone later removed the card step.

**Expected:** Publication remains blocked until that artifact exists.

## 5. Inspect identity

Retain the previous contract and explain the change. A new hash detects different bytes but cannot judge scientific validity.

The second assertion matters as much as the first: digest() uses sort_keys=True, so reversing key order produces the same hash, while changing label_horizon_hours from 4 to 24 produces a different one (the first 12 hex characters move from 60992e449952 to c2e24b0037d3 on this contract). Hashing str(contract) instead would change with key order and report a false change.

```python
# Uses digest() from main.py.
contract = {
    "unit": "one customer decision",
    "prediction_time": "cutoff",
    "feature_columns": ["usage", "tickets", "region"],
    "label": "label",
    "label_horizon_hours": 4,
    "decision": "offer optional support",
    "owner": "learning team",
}
changed = {**contract, "label_horizon_hours": 24}
assert digest(changed) != digest(contract)
assert digest(dict(reversed(list(contract.items())))) == digest(contract)
```

**Expected:** The exact identity changes.

## 6. Define ownership

A real deployment needs acknowledged owners and procedures. Keep that external qualification separate from this local fixture.

The fixture's contract has a single owner, "learning team", for everything, which is acceptable only because nothing is deployed. Split it into named reviewers for the feature list, the evaluation report and the support offer decision, and check that each node in the dependency dictionary that needs approval names one of them.

**Expected:** Responsibilities are explicit.

## Complete reference

```python
"""mle-001: local, bounded ML engineering investigation."""

import hashlib
import json

import numpy as np
import pandas as pd


def digest(data):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def dataset():
    rng = np.random.default_rng(17)
    n = 120
    usage = rng.uniform(1, 100, n)
    tickets = rng.poisson(2, n)
    region = np.where(np.arange(n) % 2 == 0, "north", "south")
    logit = 0.9 * tickets - 0.035 * usage + (region == "north") * 0.3
    probability = 1 / (1 + np.exp(-logit))
    label = (rng.random(n) < probability).astype(int)
    cutoff = np.arange(n) + 100
    return pd.DataFrame(
        {
            "id": np.arange(n),
            "customer_id": np.arange(n) % 12,
            "cutoff": cutoff,
            "available_at": cutoff - 2,
            "label_available_at": cutoff + 4,
            "usage": usage,
            "tickets": tickets,
            "region": region,
            "label": label,
        }
    )


def example_one():
    contract = {
        "unit": "one customer decision",
        "prediction_time": "cutoff",
        "feature_columns": ["usage", "tickets", "region"],
        "label": "label",
        "label_horizon_hours": 4,
        "decision": "offer optional support",
        "owner": "learning team",
    }
    frame = dataset()
    assert frame["id"].is_unique and all(
        name in frame.columns for name in contract["feature_columns"]
    )
    assert "label" not in contract["feature_columns"]
    assert (frame["label_available_at"] > frame["cutoff"]).all()
    return {"contract": contract, "records": len(frame), "contract_hash": digest(contract)}


def example_two():
    dependencies = {
        "validate": set(),
        "features": {"validate"},
        "train": {"features"},
        "evaluate": {"train"},
        "publish": {"evaluate"},
    }
    completed = {"validate", "features", "train"}
    ready = sorted(
        name
        for name, parents in dependencies.items()
        if name not in completed and parents <= completed
    )
    assert ready == ["evaluate"] and "publish" not in ready
    return {"ready": ready, "publication_requires_evaluation": True}


def main():
    print(example_one())
    print(example_two())
    print("mle-001 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Keep model fitting as one stage inside that contract, and use the later lessons to replace each local mechanism with actual inspected execution evidence.
