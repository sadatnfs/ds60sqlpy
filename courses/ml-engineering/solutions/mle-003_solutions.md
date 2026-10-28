# mle-003: explained reference

Build features at the decision grain while preserving all requests and missingness categories.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Include the current event

Choose whether the current event is observable at decision time. Do not change the operator solely to improve a model score.

**Expected:** Any changed contribution is explained.

## 2. Add an unmatched request

Left-join selected features back and add a reason or coverage flag. Excluding it silently changes the deployment scenario.

**Expected:** It remains in the final population.

## 3. Detect duplicated features

Resolve conflicting versions under a reviewed rule before joining. Arbitrary deduplication can conceal a temporal or identity defect.

**Expected:** The one-to-one contract rejects fanout.

## 4. Compare zero and null

A missing value may use a fitted imputation or abstention policy. Carry a missingness flag when its meaning matters.

**Expected:** The cases retain different meanings.

## 5. Validate counts

Track matched, missing, rejected and duplicated cases separately. Use the original population as the denominator for coverage.

**Expected:** Every request has an explained outcome.

## 6. Plan a scalable equivalent

Use an appropriate indexed, versioned or windowed implementation and compare it with the small independent oracle on boundary cases.

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

Build features at the decision grain while preserving all requests and missingness categories. Verify the temporal rule with identified rows, then use the same contract to evaluate a real feature-store implementation.
