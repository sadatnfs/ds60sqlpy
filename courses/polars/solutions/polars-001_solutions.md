# polars-001: explained reference

Construct and verify a typed table with a stated row grain.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Predict a new order

The additional revenue is 3*4=12;30+12=42. Preserve a unique order_id so row-level reconciliation remains possible.

**Expected:** The total is 42 and there are 4 order rows.

## 2. Choose a projection

Apply result.select("order_id", "revenue"). select changes the returned columns, not the number of input orders.

**Expected:** The output has 3 rows and 2 columns.

## 3. Explain an aggregate

The calculation is(10+8+12)/3. A mean per item would be 30/7 and answers a different question.

**Expected:** Mean order revenue is 10.

## 4. Keep raw state

The returned frame is a distinct transformation result. Reassigning frame=result is a deliberate choice, not an implicit mutation.

**Expected:** The assertion remains true.

## 5. State an empty policy

The result is valid under this predicate. A downstream policy may reject an empty training set, but should do so with a separate explicit check.

**Expected:** The schema remains defined and height is 0.

## 6. Validate identifiers

Assert frame["order_id"].n_unique()==frame.height when one row per order is required. A duplicate policy needs domain reasoning before aggregation.

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

Construct and verify a typed table with a stated row grain. For an independent case, use a small inventory table with units and cost, calculate stock value, and verify it with Python arithmetic. Preserve both raw and transformed frames so a reviewer can explain every changed field. This establishes a small data contract, not a guarantee that an arbitrary input file is clean.
