# polars-005: explained reference

Build an aggregate whose numerator, denominator and weighting unit are explicit.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Compute a global rate

The total is not the mean of 0.1 and 0.5 because group trial counts differ. The intended weighting unit is one trial.

**Expected:** The global rate is 11/102.

## 2. Find a zero denominator

Return null or reject it with a reason; do not silently assign rate 0, which would claim observed failures.

**Expected:** The output follows an explicit undefined-rate policy.

## 3. Change the estimand

If the target is a uniformly sampled group, averaging group rates can be appropriate. It is not the same target as a uniformly sampled trial.

**Expected:** The answer defines equal weighting of groups.

## 4. Audit row grain

Publish the keys and aggregation definitions. Carrying an arbitrary order_id after grouping would incorrectly imply an order-level result.

**Expected:** Three input rows reduce to 2 groups.

## 5. Report precision inputs

The counts support interval calculations and comparisons of evidence. Equal percentages from 1 trial and 1,000 trials do not have equal uncertainty.

**Expected:** Both components are recoverable.

## 6. Handle an all-null group

Retaining it with a null mean makes coverage explicit. Dropping it changes the population of reported groups and should be reported.

**Expected:** Its observed count remains 0.

## Complete reference

```python
"""polars-005: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "successes": [1, 9, 1], "trials": [1, 99, 2]})
    output = (
        frame.group_by("group")
        .agg(
            pl.col("successes").sum().alias("successes"),
            pl.col("trials").sum().alias("trials"),
            pl.len().alias("rows"),
        )
        .with_columns((pl.col("successes") / pl.col("trials")).alias("rate"))
        .sort("group")
    )
    assert output["rate"].to_list() == [0.1, 0.5]
    naive = (
        frame.filter(pl.col("group") == "A")
        .select((pl.col("successes") / pl.col("trials")).mean())
        .item()
    )
    assert abs(naive - 0.1) > 0.4
    return {"weighted_rates": output.to_dicts(), "wrong_equal_row_mean": naive}


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [2, None, None]})
    result = (
        frame.group_by("group")
        .agg(
            pl.len().alias("rows"),
            pl.col("value").count().alias("observed"),
            pl.col("value").mean().alias("mean"),
        )
        .sort("group")
    )
    assert result["rows"].to_list() == [2, 1]
    assert result["observed"].to_list() == [1, 0]
    assert result["mean"].to_list() == [2.0, None]
    return {"grain": "one row per group", "summary": result.to_dicts()}


def main():
    print(example_one())
    print(example_two())
    print("polars-005 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Build an aggregate whose numerator, denominator and weighting unit are explicit. Reconcile the totals independently with Python arithmetic, retain coverage counts, and then decide whether the result supports the intended comparison. Apply the same discipline to conversion rates, average losses and model-quality dashboards.
