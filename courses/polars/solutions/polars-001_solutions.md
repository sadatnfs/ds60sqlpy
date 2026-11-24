# polars-001: explained reference

Construct and verify a typed table with a stated row grain.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Predict a new order

The additional revenue is \(3 \times 4 = 12\), so the total is \(30 + 12 = 42\). Preserve a unique order_id so row-level reconciliation remains possible.

```python
import polars as pl

frame = pl.DataFrame({"order_id": [1, 2, 3], "units": [2, 1, 4], "price": [5, 8, 3]})
extra = pl.DataFrame({"order_id": [4], "units": [3], "price": [4]})
orders = pl.concat([frame, extra]).with_columns(
    (pl.col("units") * pl.col("price")).alias("revenue")
)
assert orders.height == 4
assert orders["revenue"].sum() == 42
```

**Why it holds here:** The three existing orders carry revenue 10, 8 and 12, so the base total is 30. A fourth row with units 3 and price 4 adds exactly 12 because revenue is computed per row after pl.concat stacks the frames.

**Plausible wrong approach:** Adding 3 to the units column of an existing order instead also raises the total, but it changes order 1 or 2 rather than recording a new order, so height stays 3 and per-order reconciliation breaks.

**How to verify:** Run the answer code and check orders.height == 4 and orders['revenue'].sum() == 42; the new row's revenue should be the only value equal to 12 that was not already present in the original result.

**Expected:** The total is 42 and there are 4 order rows.

## 2. Choose a projection

Apply result.select("order_id", "revenue"). select changes the returned columns, not the number of input orders.

**Why it holds here:** select keeps the expressions you name and nothing else, so result.select('order_id', 'revenue') drops units and price while every one of the 3 orders survives with its own revenue.

**Plausible wrong approach:** Using drop('units') alone leaves price in place, and writing select(pl.col('revenue').sum()) collapses the table to a single aggregate row, which no longer answers a per-order question.

**How to verify:** Check that the projected frame has shape (3, 2) and columns ['order_id', 'revenue'], and that its revenue list is still [10, 8, 12].

**Expected:** The output has 3 rows and 2 columns.

## 3. Explain an aggregate

The calculation is \((10 + 8 + 12)/3 = 10\). A mean per item would be 30/7 and answers a different question.

```python
import polars as pl

frame = pl.DataFrame({"order_id": [1, 2, 3], "units": [2, 1, 4], "price": [5, 8, 3]})
result = frame.with_columns((pl.col("units") * pl.col("price")).alias("revenue"))
# The denominator is the number of order rows (3), not the number of units (7).
assert result.select(pl.col("revenue").mean()).item() == 10.0
```

**Why it holds here:** mean over revenue divides the sum 30 by the number of order rows, 3, because each row is one order in this table. That gives 10, the average order value.

**Plausible wrong approach:** Dividing total revenue by total units (30 / 7, about 4.29) answers average price per unit, a different estimand, even though it uses the same columns.

**How to verify:** Run result.select(pl.col('revenue').mean()).item() and expect 10.0; then compute result['units'].sum() to confirm the 7 that the wrong denominator would use.

**Expected:** Mean order revenue is 10.

## 4. Keep raw state

The returned frame is a distinct transformation result. Reassigning frame=result is a deliberate choice, not an implicit mutation.

**Why it holds here:** with_columns returns a new DataFrame; frame itself still has the three original columns. The reference asserts frame.shape == (3, 3) while result.shape == (3, 4).

**Plausible wrong approach:** Expecting pandas-style in-place assignment and later reading frame['revenue'] raises a ColumnNotFoundError, because the expression was never attached to frame.

**How to verify:** After building result, assert 'revenue' not in frame.columns and 'revenue' in result.columns; both should hold.

**Expected:** The assertion remains true.

## 5. State an empty policy

The result is valid under this predicate. A downstream policy may reject an empty training set, but should do so with a separate explicit check.

**Why it holds here:** No order in this fixture reaches revenue 100, so the filter returns zero rows. example_two shows such a result keeps its schema, which is why an empty answer is still a well-typed answer.

**Plausible wrong approach:** Raising an exception inside the transformation whenever height is 0 mixes a valid query result with a downstream policy, and makes the same code unusable for exploratory filters.

**How to verify:** Filter result on pl.col('revenue') > 100 and check height == 0 and that the schema still lists order_id, units, price and revenue with their integer types.

**Expected:** The schema remains defined and height is 0.

## 6. Validate identifiers

Assert frame["order_id"].n_unique()==frame.height when one row per order is required. A duplicate policy needs domain reasoning before aggregation.

**Why it holds here:** The stated grain is one row per order, so order_id must be unique. Appending a second row with order_id 3 makes n_unique 3 while height becomes 4, which breaks the grain.

**Plausible wrong approach:** Calling unique() on the frame to remove the duplicate hides the question of which row is correct, and if the two rows differ in units it silently keeps both.

**How to verify:** Concatenate a row with order_id 3 and assert frame['order_id'].n_unique() < frame.height; frame.filter(pl.col('order_id').is_duplicated()) should list both id 3 rows.

**Expected:** n_unique is smaller than height.

## Complete reference

```python
"""polars-001: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"order_id": [1, 2, 3], "units": [2, 1, 4], "price": [5, 8, 3]})
    result = frame.with_columns((pl.col("units") * pl.col("price")).alias("revenue"))
    assert frame.shape == (3, 3) and result.shape == (3, 4)
    assert result["revenue"].to_list() == [10, 8, 12]
    assert result.select(pl.col("revenue").sum()).item() == 30
    assert "revenue" not in frame.columns
    return {"rows": result.to_dicts(), "total_revenue": 30}


def example_two():
    frame = pl.DataFrame(
        {"id": [1, 2], "label": ["new", "done"]}, schema={"id": pl.Int64, "label": pl.String}
    )
    assert frame.schema == {"id": pl.Int64, "label": pl.String}
    empty = frame.filter(pl.col("id") > 10)
    assert empty.height == 0 and empty.schema == frame.schema
    selected = frame.select("label", "id")
    assert selected.columns == ["label", "id"]
    return {"empty_shape": empty.shape, "schema": str(empty.schema)}


def main():
    print(example_one())
    print(example_two())
    print("polars-001 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

For an independent case, use a small inventory table with units and cost, calculate stock value, and verify it with Python arithmetic. Preserve both raw and transformed frames so a reviewer can explain every changed field. This establishes a small data contract, not a guarantee that an arbitrary input file is clean.
