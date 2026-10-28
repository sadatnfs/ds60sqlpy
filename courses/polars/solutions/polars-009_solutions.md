# polars-009: explained reference

Create row-preserving historical features with explicit ordering.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Shuffle the fixture

Compare results after sorting by the same keys. A result that changes with input ordering reveals an incomplete ordering contract.

**Expected:** The identified window results remain unchanged.

## 2. Add a timestamp tie

Use an event sequence identifier when available. If simultaneous events should be aggregated together, do that before a sequential window.

**Expected:** A documented tie-breaker produces a deterministic sequence.

## 3. Exclude the current event

A cumulative sum includes the current row. Shift it to represent prior history and explain whether a first event should map to zero or unknown.

**Expected:** For A it is [null, 2, 7] before an explicit first-value policy.

## 4. Check group reset

Without over(customer), a shift can cross entity boundaries. This is a common silent feature-engineering defect.

**Expected:** B has a missing predecessor.

## 5. Review training leakage

Estimate preprocessing parameters on the training partition and apply those fixed parameters to held-out data. Group calculations must follow the deployment scenario.

**Expected:** The explanation identifies which observations estimated the mean.

## 6. Compare grains

Neither shape is inherently wrong. Choose the result grain needed by the next stage and verify key identity at that boundary.

**Expected:** The count changes from 3 to 2.

## Complete reference

```python
"""polars-009: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame(
        {
            "id": [3, 1, 2, 4],
            "customer": ["A", "A", "B", "A"],
            "time": [2, 1, 1, 3],
            "value": [5, 2, 7, 4],
        }
    )
    output = frame.sort("customer", "time", "id").with_columns(
        pl.col("value").cum_sum().over("customer").alias("running"),
        pl.col("value").shift(1).over("customer").alias("previous"),
    )
    assert output["running"].to_list() == [2, 7, 11, 7]
    assert output["previous"].to_list() == [None, 2, 5, None]
    assert output.height == frame.height
    return {"ordered_windows": output.to_dicts()}


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [2.0, 6.0, 9.0]})
    centered = frame.with_columns(
        (pl.col("value") - pl.col("value").mean().over("group")).alias("centered")
    )
    assert centered["centered"].to_list() == [-2.0, 2.0, 0.0]
    assert frame.group_by("group").agg(pl.col("value").mean()).height == 2
    assert centered.height == 3
    return {"row_preserving_values": centered["centered"].to_list(), "grouped_rows": 2}


def main():
    print(example_one())
    print(example_two())
    print("polars-009 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Create row-preserving historical features with explicit ordering. Test shuffled inputs, entity boundaries and timestamp ties, then document whether each feature includes the current event. Extend the rule to an availability-time boundary before using the feature in model training.
