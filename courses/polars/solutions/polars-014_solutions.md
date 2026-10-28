# polars-014: explained reference

Reconstruct features using only information eligible at each prediction time.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Tighten freshness

This is a stricter freshness rule, not necessarily a better model. State what should happen when no feature qualifies.

**Expected:** No unequal-time feature is matched.

## 2. Add an entity key

Use the by key for grouped as-of matching or include entity identity in the candidate join. Validate sorting within each group.

**Expected:** No match crosses customer identity.

## 3. Change availability

The feature value 999 can then be selected legitimately under the fixture, though its plausibility would still require a data-quality check.

**Expected:** It becomes eligible at cutoff 5.

## 4. Test exact boundaries

The example uses <=. A production system may use an ingestion watermark or transaction boundary that needs a stricter rule.

**Expected:** It is included only under the stated inclusive policy.

## 5. Preserve unmatched requests

Retain the original request table and left-join selected features back to it. Report coverage before fitting or scoring.

**Expected:** The request remains identifiable with a missing-feature reason.

## 6. Review a feature store

Create a known late-arrival fixture and compare actual retrieval with an independently computed oracle. Record the supported semantics and any required upstream snapshot policy.

**Expected:** They concern event validity and historical availability.

## Complete reference

```python
"""polars-014: complete bounded Polars investigation."""

import polars as pl


def example_one():
    requests = pl.DataFrame({"id": [1, 2, 3], "time": [2, 5, 9]}).sort("time")
    features = pl.DataFrame({"time": [1, 4, 8], "value": [10, 20, 30]}).sort("time")
    past = requests.join_asof(features, on="time", strategy="backward", tolerance=2)
    future = requests.join_asof(features, on="time", strategy="forward")
    assert past["value"].to_list() == [10, 20, 30]
    assert future["value"].to_list() == [20, 30, None]
    return {"past_only": past.to_dicts(), "lookahead_counterexample": future.to_dicts()}


def example_two():
    requests = pl.DataFrame({"request": [1, 2], "customer": [10, 10], "cutoff": [5, 9]})
    features = pl.DataFrame(
        {"customer": [10, 10, 10], "event": [2, 4, 8], "known": [3, 7, 8], "value": [10, 999, 30]}
    )
    candidates = requests.join(features, on="customer").filter(
        (pl.col("event") <= pl.col("cutoff")) & (pl.col("known") <= pl.col("cutoff"))
    )
    correct = (
        candidates.sort("request", "event", "known").group_by("request", maintain_order=True).last()
    )
    assert correct["value"].to_list() == [10, 30]
    leaking = (
        requests.join(features, on="customer")
        .filter(pl.col("event") <= pl.col("cutoff"))
        .sort("request", "event")
        .group_by("request", maintain_order=True)
        .last()
    )
    assert leaking["value"].to_list() == [999, 30]
    return {"available_values": [10, 30], "event_time_only_values": [999, 30]}


def main():
    print(example_one())
    print(example_two())
    print("polars-014 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Reconstruct features using only information eligible at each prediction time. Test a late arrival, a stale feature, a timestamp tie and an unmatched request. Carry those semantics into the later Feast and ML engineering lessons, where library behavior is checked against explicit temporal fixtures.
