# mle-002: explained reference

Construct an eligible training cohort from explicit feature and label clocks.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change knowledge time

Record the new source history and its identity. Retrospective conclusions depend on which version of history is being used.

Moving record 2 to known_at 4 (or 5) makes it pass both conditions at cutoff 5, and because select() keeps the latest event_at, 999 replaces 10. The answer code asserts [select(5), select(9)] == [999, 30]; cutoff 9 still returns 30 because event 8 is newer. Editing value instead of known_at would test nothing about eligibility. Keep the old record list too, since a model trained on the first history saw 10, not 999.

```python
records = [
    {"id": 1, "event_at": 2, "known_at": 3, "value": 10},
    {"id": 2, "event_at": 4, "known_at": 4, "value": 999},
    {"id": 3, "event_at": 8, "known_at": 8, "value": 30},
]


def select(cutoff):
    valid = [r for r in records if r["event_at"] <= cutoff and r["known_at"] <= cutoff]
    return max(valid, key=lambda r: (r["event_at"], r["known_at"]))["value"]


assert [select(5), select(9)] == [999, 30]
```

**Expected:** It becomes eligible under the same rule.

## 2. Test an exact boundary

A transaction or ingestion watermark may require a stricter operational rule. State and test that rule explicitly.

The second snippet sets known_at to 5 with cutoff 5 and expects ids [1, 2]. If the filter used known_at < cutoff, id 2 would drop and the list would be [1]; that stricter rule is right when a value written at second 5 may not be readable by a query at second 5. Pick one operator, write it into the contract, and add an assertion at exactly the boundary so a later refactor cannot change it silently.

```python
records = [
    {"id": 1, "event_at": 2, "known_at": 3, "value": 10},
    {"id": 2, "event_at": 4, "known_at": 5, "value": 999},
    {"id": 3, "event_at": 8, "known_at": 8, "value": 30},
]
cutoff = 5
valid = [r for r in records if r["event_at"] <= cutoff and r["known_at"] <= cutoff]
assert [r["id"] for r in valid] == [1, 2]
```

**Expected:** The example includes it under <=.

## 3. Change the training cutoff

Recompute the eligible identifiers and report them. Training and evaluation should retain the cutoff that produced their cohorts.

At cutoff 181 the candidate rows are ids 0 to 80 (81 rows) and maturity requires id + 104 <= 181, so ids 0 to 77 qualify: 78 mature rows, with 78, 79 and 80 still waiting. The answer code checks that exactly id 77 joins. A common mistake is to filter only on cutoff < training_cutoff, which returns 81 rows and treats three unknown labels as observed.

```python
# Uses dataset() from main.py.
frame = dataset()
cohorts = {}
for training_cutoff in (180, 181):
    mature = frame[(frame.cutoff < training_cutoff) & (frame.label_available_at <= training_cutoff)]
    cohorts[training_cutoff] = set(mature.id)
assert len(cohorts[180]) == 77
assert cohorts[180] <= cohorts[181]
assert cohorts[181] - cohorts[180] == {77}
```

**Expected:** The label-maturity cohort changes predictably.

## 4. Identify a leakage field

Examples include later resolution, future aggregate and final status. Verify availability against system behavior, not the label chosen by a data author.

In this dataset label_available_at itself is the clearest example: it is computed as cutoff + 4 and is never known at cutoff. A field like a count of tickets in the four hours after the decision would leak the same way. Verify a candidate by asserting its availability column is <= cutoff for every training row.

**Expected:** The answer explains when it becomes available.

## 5. Preserve missing outcomes

Wait for maturity or use an explicit censoring/selection model. Keep label coverage visible in monitoring.

With cutoff 180, ids 77, 78 and 79 have labels arriving at 181, 182 and 183. Filling them with 0 would add three negatives to a fixture whose positive rate is about 0.48, biasing the newest period downward exactly where drift would first appear. Report 77 labeled and 3 pending instead.

**Expected:** The answer separates unknown from negative.

## 6. Transfer to timestamps

Avoid naive/local-time ambiguity and test boundary timestamps. Preserve event and availability columns separately.

Convert by anchoring hour 0 to a UTC instant and adding pd.to_timedelta(hours, "h"); compare tz-aware columns only. Verify that the mature cohort at the converted training cutoff is still 77 rows. Mixing naive and aware timestamps raises in pandas, and localizing to a zone with daylight saving can shift a boundary by an hour.

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

Demonstrate a late-known counterexample and retain excluded identities. Apply these boundaries consistently to model selection, monitoring and feature-store retrieval.
