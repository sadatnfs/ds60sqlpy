# polars-009: explained reference

Create row-preserving historical features with explicit ordering.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Shuffle the fixture

Compare results after sorting by the same keys. A result that changes with input ordering reveals an incomplete ordering contract.

**Why it holds here:** The explicit sort by customer, time and id rebuilds the same row order whatever order the input arrives in, so running and previous do not depend on file order.

**Plausible wrong approach:** Dropping the sort makes the running total follow arrival order, and the fixture already lists id 3 before id 1, so A would read [5, 7, 11] instead of [2, 7, 11].

**How to verify:** Shuffle the fixture with sample(fraction=1.0, shuffle=True, seed=1), rerun, sort both outputs by id and assert they are equal.

**Expected:** The identified window results remain unchanged.

## 2. Add a timestamp tie

Use an event sequence identifier when available. If simultaneous events should be aggregated together, do that before a sequential window.

**Why it holds here:** Two A events at time 2 have no natural order, so id acts as the documented tie breaker and the cumulative sum steps through them in id order every run.

**Plausible wrong approach:** Sorting on customer and time alone leaves the tied pair in whatever order the sort returns, so the intermediate running value for each tied row can swap between runs.

**How to verify:** Add an A event with id 5 at time 2, sort with and without id, and check that only the version including id has a fixed running sequence for both rows.

**Expected:** A documented tie-breaker produces a deterministic sequence.

## 3. Exclude the current event

A cumulative sum includes the current row. Shift it to represent prior history and explain whether a first event should map to zero or unknown.

```python
import polars as pl

frame = pl.DataFrame(
    {
        "id": [3, 1, 2, 4],
        "customer": ["A", "A", "B", "A"],
        "time": [2, 1, 1, 3],
        "value": [5, 2, 7, 4],
    }
)
output = frame.sort("customer", "time", "id").with_columns(
    pl.col("value").cum_sum().shift(1).over("customer").alias("running_before")
)
assert output.filter(pl.col("customer") == "A")["running_before"].to_list() == [None, 2, 7]
```

**Why it holds here:** cum_sum includes the current row, so A's values 2, 5 and 4 produce 2, 7 and 11; shift(1) inside over moves that history down one row to [None, 2, 7].

**Plausible wrong approach:** Applying shift(1) outside over lets the first A row inherit the final value from the preceding customer in the sorted frame.

**How to verify:** Run the answer code and assert A's running_before equals [None, 2, 7]; B's only row should also be None.

**Expected:** For A it is [null, 2, 7] before an explicit first-value policy.

## 4. Check group reset

Without over(customer), a shift can cross entity boundaries. This is a common silent feature-engineering defect.

**Why it holds here:** over('customer') restarts each window for every customer, so B's single event gets no predecessor: previous is None and running restarts at 7.

**Plausible wrong approach:** Calling pl.col('value').shift(1) without over makes B's row read A's last value 4 in the sorted frame, a cross customer leak.

**How to verify:** In example_one the previous column is [None, 2, 5, None]; the final None is B's row and confirms the reset.

**Expected:** B has a missing predecessor.

## 5. Review training leakage

Estimate preprocessing parameters on the training partition and apply those fixed parameters to held-out data. Group calculations must follow the deployment scenario.

**Why it holds here:** A group mean computed over all rows uses the held out rows too, so each training feature already contains information from the validation partition.

**Plausible wrong approach:** Splitting after centering looks harmless because the code is identical, but the mean used for A, which is 4.0 in the fixture, would shift once validation rows are excluded.

**How to verify:** Compute the group mean from the training rows only, apply it to validation, and compare with the full data mean; any difference shows the leak's size.

**Expected:** The explanation identifies which observations estimated the mean.

## 6. Compare grains

Neither shape is inherently wrong. Choose the result grain needed by the next stage and verify key identity at that boundary.

```python
import polars as pl

frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [2.0, 6.0, 9.0]})
window = frame.with_columns(pl.col("value").mean().over("group").alias("group_mean"))
grouped = frame.group_by("group").agg(pl.col("value").mean().alias("group_mean"))
assert (window.height, grouped.height) == (3, 2)
```

**Why it holds here:** The window form attaches group_mean to every original row, so height stays 3; group_by returns one row per group, so height falls to 2.

**Plausible wrong approach:** Joining the grouped result back without noting the grain change can duplicate rows if the group key is not unique on one side.

**How to verify:** Run the answer code and assert (window.height, grouped.height) == (3, 2), with A's mean 4.0 and B's 9.0 in both.

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

Test shuffled inputs, entity boundaries and timestamp ties, then document whether each feature includes the current event. Extend the rule to an availability-time boundary before using the feature in model training.
