# polars-013: explained reference

Normalize nested events with an explicit population and identity contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Separate empty from unknown

Use is_null and an explicit length comparison. Keep these categories separate in a coverage report.

**Expected:** There is one of each.

## 2. Change the grain

Add a stable item position or item identifier when the source contract supports it. A repeated label is not necessarily a duplicate item.

**Expected:** An order_id alone is no longer sufficient.

## 3. Keep order-level metrics

Item counts and order counts answer different questions. Retain an order-level table for denominators and join it carefully when summarizing items.

**Expected:** The count remains 3.

## 4. Add a struct field

A schema version should explain the added field and its units. Positional unpacking can silently change meaning when fields are reordered.

**Expected:** All values and field names are preserved.

## 5. Transform a nested value

pl.element()*pl.element() expresses the operation within each list. It preserves the list boundaries while changing the values.

**Expected:** The lists become [[1,4],[9]].

## 6. Test null nested elements

Decide whether the collection is partially observed, invalid or imputable. Do not erase the distinction merely to simplify a numeric aggregation.

**Expected:** The null remains visible unless explicitly handled.

## Complete reference

```python
"""polars-013: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"order": [1, 2, 3], "items": [["a", "b"], [], None]})
    normalized = frame.with_columns(pl.col("items").list.len().alias("count"))
    assert normalized["count"].to_list() == [2, 0, None]
    eligible = normalized.filter(pl.col("count") > 0).explode("items")
    assert eligible.to_dicts() == [
        {"order": 1, "items": "a", "count": 2},
        {"order": 1, "items": "b", "count": 2},
    ]
    return {"order_rows": 3, "item_rows": 2, "excluded_empty_or_unknown_orders": [2, 3]}


def example_two():
    frame = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
    packed = frame.select(pl.struct("x", "y").alias("point"))
    extracted = packed.select(pl.col("point").struct.field("x"), pl.col("point").struct.field("y"))
    assert extracted.equals(frame)
    evaluated = pl.DataFrame({"values": [[1, 2], [3]]}).select(
        pl.col("values").list.eval(pl.element() * 2).alias("doubled")
    )
    assert evaluated["doubled"].to_list() == [[2, 4], [6]]
    return {"struct_round_trip": True, "nested_values": evaluated.to_dicts()}


def main():
    print(example_one())
    print(example_two())
    print("polars-013 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Normalize nested events with an explicit population and identity contract. Demonstrate empty, missing and repeated-element cases, then verify that any flattened table can still be related to its original records. This is essential for reliable event analytics and sequence-feature construction.
