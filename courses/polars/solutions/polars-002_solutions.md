# polars-002: explained reference

Build a transformation whose dependency stages are explicit.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change the increment

Use two with_columns calls and verify the final values; changing argument order inside one call does not create this dependency.

**Why it holds here:** Expressions in one with_columns call all read the input frame, so x * 10 there still sees 1, 2, 3. A second with_columns call reads the frame produced by the first, where x is 3, 4, 5, and gives 30, 40, 50.

**Plausible wrong approach:** Putting (pl.col('x') + 2).alias('x') first and the multiplication second inside the same call still multiplies the original x, giving [10, 20, 30].

**How to verify:** Chain frame.with_columns((pl.col('x') + 2).alias('x')).with_columns((pl.col('x') * 10).alias('scaled')) and assert scaled is [30, 40, 50].

**Expected:** The staged values are [30, 40, 50].

## 2. Name the old value

Compute (pl.col("x")+1).alias("incremented_x"). Retaining both fields makes a later comparison or audit straightforward.

```python
import polars as pl

frame = pl.DataFrame({"x": [1, 2, 3]})
output = frame.with_columns((pl.col("x") + 1).alias("incremented_x"))
assert output.to_dict(as_series=False) == {"x": [1, 2, 3], "incremented_x": [2, 3, 4]}
```

**Why it holds here:** Giving the incremented expression a new alias leaves x untouched, so both the original 1, 2, 3 and the new 2, 3, 4 sit side by side for comparison.

**Plausible wrong approach:** Aliasing the result as x overwrites the original values, which is what example_one does and is fine only when the old value is no longer needed.

**How to verify:** Assert output.to_dict(as_series=False) equals {'x': [1, 2, 3], 'incremented_x': [2, 3, 4]}.

**Expected:** Both x and incremented_x are visible.

## 3. Remove ambiguity

Use pl.lit("paid").alias("label") in with_columns. In select alone a scalar literal is a one-row result, which is a different context.

**Why it holds here:** In with_columns a literal is broadcast to every row, so label becomes paid for all three rows. In select alone it produces a single-row frame, which example_two shows with item().

**Plausible wrong approach:** Writing frame.select(pl.lit('paid')) and joining it back assumes it has three rows, but it has one.

**How to verify:** Run frame.with_columns(pl.lit('paid').alias('label')) and check label.to_list() equals ['paid', 'paid', 'paid'] and height is 3.

**Expected:** Every returned value is the string paid.

## 4. Change a business condition

Paid rows contribute 5+11 and pending contributes 7/2. State the policy; the query engine cannot decide when revenue should be recognized.

**Why it holds here:** The when chain maps paid rows to amount and pending rows to amount / 2, so recognized becomes 5, 3.5, 11 and the total is 19.5. The half-value rule is the policy, not a Polars default.

**Plausible wrong approach:** Using otherwise(0) as in example_two keeps the 16 total, and using integer division would turn 7 / 2 into 3 instead of 3.5.

**How to verify:** Sum the new column and expect 19.5; check that the recognized column dtype is Float64 because one branch divides.

**Expected:** The fixture total becomes 19.5.

## 5. Break a dependency

Add another with_columns stage. Suppressing the error or creating a null field would change the intended calculation.

**Why it holds here:** Inside one with_columns call the alias y does not exist yet, because each expression reads the input frame. Referencing pl.col('y') in the same call fails.

**Plausible wrong approach:** Wrapping the reference in a fill_null or try block makes the error vanish but replaces the intended dependent value with something unrelated.

**How to verify:** Run frame.with_columns((pl.col('x') + 1).alias('y'), (pl.col('y') * 10).alias('z')) and expect pl.exceptions.ColumnNotFoundError mentioning y.

**Expected:** A missing-column error identifies the unavailable alias.

## 6. Compare two implementations

Filtering paid rows then summing amount matches the conditional sum. It does not return the same row-level table, because pending rows have been removed.

```python
import polars as pl

frame = pl.DataFrame({"status": ["paid", "pending", "paid"], "amount": [5, 7, 11]})
conditional = frame.select(
    pl.when(pl.col("status") == "paid").then(pl.col("amount")).otherwise(0).sum()
).item()
filtered = frame.filter(pl.col("status") == "paid").select(pl.col("amount").sum()).item()
assert conditional == filtered == 16
```

**Why it holds here:** The conditional sum keeps all three rows and zeroes pending, while the filtered sum removes pending first. Both arrive at 5 plus 11, which is 16.

**Plausible wrong approach:** Assuming the filtered version also returns a table aligned with the input is wrong; it has 2 rows, not 3.

**How to verify:** Run the answer code and assert conditional == filtered == 16, then compare frame.filter(...).height (2) with frame.height (3).

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

Apply the same reasoning to feature pipelines: a normalized value should reference the intended cleaned field, and training and serving must agree on that order. Use intermediate schemas and a small hand-calculated fixture to review the pipeline before optimizing it.
