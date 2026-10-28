# mle-001: explained reference

Define an ML product through its decision, information boundary and accepted artifacts.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Name the population

State the unit, eligibility and time boundary. A change from repeat customers to unseen customers changes the learning problem.

**Expected:** The answer identifies synthetic customer decisions.

## 2. Exclude the target

Validate a reviewed allowlist, not every non-null column. Other leakage fields such as future status or post-decision aggregates need the same review.

**Expected:** The target cannot enter training inputs accidentally.

## 3. Change the horizon

Update the label construction and availability contract, then revalidate training/evaluation cohorts. A title change alone does not implement a new target.

**Expected:** Labels, maturity rules and evaluation need review.

## 4. Add a dependency

Add a reviewed node and prerequisite. Do not mark it complete merely because training produced a file.

**Expected:** Publication remains blocked until that artifact exists.

## 5. Inspect identity

Retain the previous contract and explain the change. A new hash detects different bytes but cannot judge scientific validity.

**Expected:** The exact identity changes.

## 6. Define ownership

A real deployment needs acknowledged owners and procedures. Keep that external qualification separate from this local fixture.

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

Define an ML product through its decision, information boundary and accepted artifacts. Keep model fitting as one stage inside that contract, and use the later lessons to replace each local mechanism with actual inspected execution evidence.
