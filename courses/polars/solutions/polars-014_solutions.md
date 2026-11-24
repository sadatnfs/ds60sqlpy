# polars-014: explained reference

Reconstruct features using only information eligible at each prediction time.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Tighten freshness

This is a stricter freshness rule, not necessarily a better model. State what should happen when no feature qualifies.

```python
import polars as pl

requests = pl.DataFrame({"id": [1, 2, 3], "time": [2, 5, 9]}).sort("time")
features = pl.DataFrame({"time": [1, 4, 8], "value": [10, 20, 30]}).sort("time")
exact = requests.join_asof(features, on="time", strategy="backward", tolerance=0)
assert exact["value"].to_list() == [None, None, None]
```

**Why it holds here:** With tolerance 0, a backward as-of match must share the request time exactly; requests 2, 5 and 9 have no feature at those times, so every value is null.

**Plausible wrong approach:** Reading the nulls as a bug and loosening tolerance back to 2 changes the freshness rule instead of deciding what to do with stale requests.

**How to verify:** Run the answer code: values are [None, None, None], compared with [10, 20, 30] at tolerance 2 in example_one.

**Expected:** No unequal-time feature is matched.

## 2. Add an entity key

Use the by key for grouped as-of matching or include entity identity in the candidate join. Validate sorting within each group.

**Why it holds here:** Passing by='customer' to join_asof restricts each search to rows of the same customer, so a request for customer 10 at time 5 cannot pick a customer 20 feature at time 4.

**Plausible wrong approach:** Running the as-of join on time alone matches the nearest earlier row of any customer, which looks correct whenever customers do not overlap in time.

**How to verify:** Build two customers with interleaved times, join with and without by, and assert every matched row has request customer equal to feature customer only in the by version.

**Expected:** No match crosses customer identity.

## 3. Change availability

The feature value 999 can then be selected legitimately under the fixture, though its plausibility would still require a data-quality check.

```python
import polars as pl

requests = pl.DataFrame({"request": [1, 2], "customer": [10, 10], "cutoff": [5, 9]})
features = pl.DataFrame(
    {"customer": [10, 10, 10], "event": [2, 4, 8], "known": [3, 4, 8], "value": [10, 999, 30]}
)
available = (
    requests.join(features, on="customer")
    .filter((pl.col("event") <= pl.col("cutoff")) & (pl.col("known") <= pl.col("cutoff")))
    .sort("request", "event", "known")
    .group_by("request", maintain_order=True)
    .last()
)
assert available["value"].to_list() == [999, 30]
```

**Why it holds here:** With known moved to 4, the revised value 999 satisfies event 4 <= 5 and known 4 <= 5, so it is legitimately available at cutoff 5 and becomes the latest row for request 1.

**Plausible wrong approach:** Removing the known filter gives the same [999, 30] here, but example_two shows that version also returns 999 when known is 7, which is the leak.

**How to verify:** Run the answer code and assert [999, 30]; then set known back to 7 and confirm the correct filter returns [10, 30].

**Expected:** It becomes eligible at cutoff 5.

## 4. Test exact boundaries

The example uses <=. A production system may use an ingestion watermark or transaction boundary that needs a stricter rule.

**Why it holds here:** The filter uses known <= cutoff, so a feature known at exactly 5 is included for cutoff 5. Under a strict < rule it would be excluded.

**Plausible wrong approach:** Mixing a strict rule in training with an inclusive rule at serving time gives features one tick fresher in one setting than the other.

**How to verify:** Set one known value equal to a cutoff and run both <= and < filters; the row should appear only under the inclusive one.

**Expected:** It is included only under the stated inclusive policy.

## 5. Preserve unmatched requests

Retain the original request table and left-join selected features back to it. Report coverage before fitting or scoring.

**Why it holds here:** A request with cutoff 1 has no feature with event and known at or before 1, so the inner join plus filter drops it entirely.

**Plausible wrong approach:** Reporting coverage from the filtered candidates counts only requests that matched, so the missing request is invisible rather than flagged.

**How to verify:** Left join the selected features back onto requests, assert the height equals the request count, and check the new request has a null value with a reason column such as no_feature_available.

**Expected:** The request remains identifiable with a missing-feature reason.

## 6. Review a feature store

Create a known late-arrival fixture and compare actual retrieval with an independently computed oracle. Record the supported semantics and any required upstream snapshot policy.

**Why it holds here:** The two questions are whether the value was valid for that event time and whether the store would have returned it at the cutoff, mirroring the event and known filters here.

**Plausible wrong approach:** Testing only that the store returns the latest value for each key passes even when that value arrived after the cutoff.

**How to verify:** Load the 999 late revision into the store, request at cutoff 5, and compare with the independently computed answer of 10.

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

Test a late arrival, a stale feature, a timestamp tie and an unmatched request. Carry those semantics into the later Feast and ML engineering lessons, where library behavior is checked against explicit temporal fixtures.
