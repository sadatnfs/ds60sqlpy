# mle-003: explained reference

Build features at the decision grain while preserving all requests and missingness categories.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Include the current event

Choose whether the current event is observable at decision time. Do not change the operator solely to improve a model score.

Changing time < cutoff to time <= cutoff alters nothing in this fixture: request 10 at cutoff 4 already sees time 1 only (time 3 is known at 5), request 11 at cutoff 9 sees times 1, 3 and 8, and request 12 at cutoff 4 sees time 2. To make the operator observable, add an event for customer 1 at time 4 with known 4; under <= request 10's sum grows by that amount and its count becomes 2. Concluding that the operator does not matter from the unchanged totals is the mistake this task exposes.

**Expected:** Any changed contribution is explained.

## 2. Add an unmatched request

Left-join selected features back and add a reason or coverage flag. Excluding it silently changes the deployment scenario.

Add request 13 for customer 3, who has no events. The inner join drops it before group_by, so totals still has three rows and nothing warns you. Joining totals back to requests with how="left" restores four rows with sum and count null for 13; fill count with 0 only if "no eligible events" is the intended meaning, and keep a has_history flag. Verify that the final height equals requests.height.

**Expected:** It remains in the final population.

## 3. Detect duplicated features

Resolve conflicting versions under a reviewed rule before joining. Arbitrary deduplication can conceal a temporal or identity defect.

In example_two, give selected two rows for request 2, say values 4.0 and 5.0. validate="1:1" raises before producing a frame, which is the desired failure. Calling unique(subset="request") first would keep one arbitrary row and pass, hiding whether 5.0 was a late revision or a key collision. Decide by known time, as in the eligibility rule, then re-run the join.

**Expected:** The one-to-one contract rejects fanout.

## 4. Compare zero and null

A missing value may use a fitted imputation or abstention policy. Carry a missingness flag when its meaning matters.

Request 1 has value 0.0, meaning history exists and sums to zero; request 3 has null, meaning no history. fill_null(0) would make them identical and the coverage of 2/3 would become an apparent 3/3. Keep the null, add is_missing, and assert joined["value"].null_count() == 1.

**Expected:** The cases retain different meanings.

## 5. Validate counts

Track matched, missing, rejected and duplicated cases separately. Use the original population as the denominator for coverage.

For example_one the inner join produces 7 candidate rows (3 for request 10, 3 for 11, 1 for 12) and the filter keeps 5, yet the population is 3 requests. Counting rows after the join would report 7 or 5, neither of which is a request count. Reconcile with n_requests == matched + no_history + rejected and compute coverage over 3.

**Expected:** Every request has an explained outcome.

## 6. Plan a scalable equivalent

Use an appropriate indexed, versioned or windowed implementation and compare it with the small independent oracle on boundary cases.

The join on customer multiplies every request by every event of that customer, so cost grows with requests times history length. Sort events by customer and known, then restrict each request to rows with known <= cutoff through a range join or a partitioned index before applying time < cutoff. A single join_asof is not enough on its own here, because it returns one nearest row and the rule has two clocks. Verify the replacement by running both on this fixture and on the time-4 boundary row from task 1; the totals must be equal.

**Expected:** The proposal preserves the same eligibility rule.

## Complete reference

```python
"""mle-003: local, bounded ML engineering investigation."""


def example_one():
    import polars as pl

    events = pl.DataFrame(
        {
            "customer": [1, 1, 1, 2],
            "time": [1, 3, 8, 2],
            "known": [1, 5, 8, 2],
            "amount": [2, 4, 9, 3],
        }
    )
    requests = pl.DataFrame({"request": [10, 11, 12], "customer": [1, 1, 2], "cutoff": [4, 9, 4]})
    eligible = requests.join(events, on="customer").filter(
        (pl.col("time") < pl.col("cutoff")) & (pl.col("known") <= pl.col("cutoff"))
    )
    totals = (
        eligible.group_by("request")
        .agg(pl.col("amount").sum().alias("sum"), pl.len().alias("count"))
        .sort("request")
    )
    assert totals.to_dicts() == [
        {"request": 10, "sum": 2, "count": 1},
        {"request": 11, "sum": 15, "count": 3},
        {"request": 12, "sum": 3, "count": 1},
    ]
    return {"features": totals.to_dicts(), "event_end_is_exclusive": True}


def example_two():
    import polars as pl

    requests = pl.DataFrame({"request": [1, 2, 3]})
    selected = pl.DataFrame({"request": [1, 2], "value": [0.0, 4.0]})
    joined = requests.join(selected, on="request", how="left", validate="1:1")
    assert joined["value"].to_list() == [0.0, 4.0, None]
    assert joined.height == 3
    return {"zero_and_missing_are_distinct": True, "coverage": 2 / 3}


def main():
    print(example_one())
    print(example_two())
    print("mle-003 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Verify the temporal rule with identified rows, then use the same contract to evaluate a real feature-store implementation.
