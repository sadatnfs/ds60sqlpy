# polars-002: explained reference

Build a transformation whose dependency stages are explicit.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change the increment

Use two with_columns calls and verify the final values; changing argument order inside one call does not create this dependency.

**Expected:** The staged values are[30,40,50].

## 2. Name the old value

Compute (pl.col("x")+1).alias("incremented_x"). Retaining both fields makes a later comparison or audit straightforward.

**Expected:** Both x and incremented_x are visible.

## 3. Remove ambiguity

Use pl.lit("paid").alias("label") in with_columns. In select alone a scalar literal is a one-row result, which is a different context.

**Expected:** Every returned value is the string paid.

## 4. Change a business condition

Paid rows contribute 5+11 and pending contributes 7/2. State the policy; the query engine cannot decide when revenue should be recognized.

**Expected:** The fixture total becomes 19.5.

## 5. Break a dependency

Add another with_columns stage. Suppressing the error or creating a null field would change the intended calculation.

**Expected:** A missing-column error identifies the unavailable alias.

## 6. Compare two implementations

Filtering paid rows then summing amount matches the conditional sum. It does not return the same row-level table, because pending rows have been removed.

**Expected:** The paid total is 16 in both implementations.

## Complete reference

```python
"""polars-002: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"x": [1, 2, 3]})
    output = frame.with_columns(
        (pl.col("x") + 1).alias("x"), (pl.col("x") * 10).alias("old_x_times_ten")
    )
    assert output.to_dict(as_series=False) == {"x": [2, 3, 4], "old_x_times_ten": [10, 20, 30]}
    sequential = frame.with_columns((pl.col("x") + 1).alias("x")).with_columns(
        (pl.col("x") * 10).alias("new_x_times_ten")
    )
    assert sequential["new_x_times_ten"].to_list() == [20, 30, 40]
    return {"parallel_context": output.to_dicts(), "explicit_dependency": sequential.to_dicts()}


def example_two():
    frame = pl.DataFrame({"status": ["paid", "pending", "paid"], "amount": [5, 7, 11]})
    output = frame.select(
        pl.when(pl.col("status") == pl.lit("paid"))
        .then(pl.col("amount"))
        .otherwise(pl.lit(0))
        .alias("recognized")
    )
    assert output["recognized"].to_list() == [5, 0, 11]
    assert frame.select(pl.lit("paid").alias("literal")).item() == "paid"
    try:
        frame.select(pl.col("missing"))
    except pl.exceptions.ColumnNotFoundError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"recognized": output.to_dicts(), "missing_column_rejected": rejected}


def main():
    print(example_one())
    print(example_two())
    print("polars-002 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Build a transformation whose dependency stages are explicit. Apply the same reasoning to feature pipelines: a normalized value should reference the intended cleaned field, and training and serving must agree on that order. Use intermediate schemas and a small hand-calculated fixture to review the pipeline before optimizing it.
