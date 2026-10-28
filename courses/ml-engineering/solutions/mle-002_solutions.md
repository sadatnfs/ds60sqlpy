# mle-002: explained reference

Construct an eligible training cohort from explicit feature and label clocks.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change knowledge time

Record the new source history and its identity. Retrospective conclusions depend on which version of history is being used.

**Expected:** It becomes eligible under the same rule.

## 2. Test an exact boundary

A transaction or ingestion watermark may require a stricter operational rule. State and test that rule explicitly.

**Expected:** The example includes it under <=.

## 3. Change the training cutoff

Recompute the eligible identifiers and report them. Training and evaluation should retain the cutoff that produced their cohorts.

**Expected:** The label-maturity cohort changes predictably.

## 4. Identify a leakage field

Examples include later resolution, future aggregate and final status. Verify availability against system behavior, not the label chosen by a data author.

**Expected:** The answer explains when it becomes available.

## 5. Preserve missing outcomes

Wait for maturity or use an explicit censoring/selection model. Keep label coverage visible in monitoring.

**Expected:** The answer separates unknown from negative.

## 6. Transfer to timestamps

Avoid naive/local-time ambiguity and test boundary timestamps. Preserve event and availability columns separately.

**Expected:** The same eligibility decisions are retained.

## Complete reference

```python
"""mle-002: local, bounded ML engineering investigation."""

import numpy as np
import pandas as pd


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
    records = [
        {"id": 1, "event_at": 2, "known_at": 3, "value": 10},
        {"id": 2, "event_at": 4, "known_at": 7, "value": 999},
        {"id": 3, "event_at": 8, "known_at": 8, "value": 30},
    ]

    def select(cutoff):
        valid = [r for r in records if r["event_at"] <= cutoff and r["known_at"] <= cutoff]
        return max(valid, key=lambda r: (r["event_at"], r["known_at"]))["value"]

    assert [select(5), select(9)] == [10, 30]
    assert (
        max([r for r in records if r["event_at"] <= 5], key=lambda r: r["event_at"])["value"] == 999
    )
    return {"eligible": [10, 30], "event_only_leak": 999}


def example_two():
    frame = dataset()
    training_cutoff = 180
    mature = frame[(frame.cutoff < training_cutoff) & (frame.label_available_at <= training_cutoff)]
    premature = frame[frame.cutoff < training_cutoff]
    assert len(mature) == 77 and len(premature) == 80
    assert set(premature.id) - set(mature.id) == {77, 78, 79}
    return {"mature_training_rows": 77, "not_yet_known_labels": [77, 78, 79]}


def main():
    print(example_one())
    print(example_two())
    print("mle-002 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Construct an eligible training cohort from explicit feature and label clocks. Demonstrate a late-known counterexample and retain excluded identities. Apply these boundaries consistently to model selection, monitoring and feature-store retrieval.
