# polars-013: explained reference

Normalize nested events with an explicit population and identity contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Separate empty from unknown

Use is_null and an explicit length comparison. Keep these categories separate in a coverage report.

```python
import polars as pl

frame = pl.DataFrame({"order": [1, 2, 3], "items": [["a", "b"], [], None]})
counts = frame.select(
    (pl.col("items").list.len() == 0).sum().alias("empty_lists"),
    pl.col("items").is_null().sum().alias("null_lists"),
)
assert counts.row(0) == (1, 1)
```

**Why it holds here:** Order 2 has an empty list, so list.len() returns 0; order 3 has a null list, so its length is null and only is_null catches it. Each test counts one order.

**Plausible wrong approach:** Using list.len() == 0 alone and treating its null result as 0 merges order 3 into the empty bucket and reports two empty orders and no unknown ones.

**How to verify:** Run the answer code and assert counts.row(0) == (1, 1); example_one also shows the lengths as [2, 0, None].

**Expected:** There is one of each.

## 2. Change the grain

Add a stable item position or item identifier when the source contract supports it. A repeated label is not necessarily a duplicate item.

**Why it holds here:** After explode, order 1 produces two rows, a and b, so order alone repeats. A position within the list, added with int_ranges or a with_row_index per order, makes (order, position) unique.

**Plausible wrong approach:** Using (order, item) as the key fails as soon as one order lists the same item twice, since two real purchases then look like a duplicate.

**How to verify:** Explode the fixture with a position column and assert select('order', 'position').is_unique().all(), while order alone is not unique.

**Expected:** An order_id alone is no longer sufficient.

## 3. Keep order-level metrics

Item counts and order counts answer different questions. Retain an order-level table for denominators and join it carefully when summarizing items.

```python
import polars as pl

frame = pl.DataFrame({"order": [1, 2, 3], "items": [["a", "b"], [], None]})
orders_before = frame.select(pl.col("order").n_unique()).item()
exploded = frame.explode("items")
assert orders_before == 3
# On polars 2.1.0 explode drops the empty-list order and keeps the null list as one null row.
assert exploded["order"].to_list() == [1, 1, 3]
```

**Why it holds here:** Counting orders before explode gives 3 because each input row is one order. Afterwards the order column reads [1, 1, 3]: order 2 disappeared and order 1 appears twice.

**Plausible wrong approach:** Counting rows of the exploded table as orders gives 3 by coincidence here, yet it includes order 1 twice and omits order 2, so the right number arrives for the wrong reason.

**How to verify:** Run the answer code: orders_before is 3 and exploded['order'] is [1, 1, 3], then add a third item to order 1 and watch the exploded count drift to 4.

**Expected:** The count remains 3.

## 4. Add a struct field

A schema version should explain the added field and its units. Positional unpacking can silently change meaning when fields are reordered.

**Why it holds here:** Fields in a struct are addressed by name, so adding z next to x and y and extracting struct.field('x'), 'y' and 'z' restores the original three columns.

**Plausible wrong approach:** Unpacking struct values by position, for example from to_dicts to a tuple, silently swaps meanings if the next version stores z first.

**How to verify:** Pack x, y and z with pl.struct, extract all three by name, and assert the result equals the input frame, as example_two does for two fields.

**Expected:** All values and field names are preserved.

## 5. Transform a nested value

pl.element()*pl.element() expresses the operation within each list. It preserves the list boundaries while changing the values.

**Why it holds here:** list.eval applies pl.element() * pl.element() inside each list, so [1, 2] becomes [1, 4] and [3] becomes [9] while each row keeps its own list.

**Plausible wrong approach:** Exploding, squaring and grouping back works but needs a row key and can reorder or drop empty lists; a map_elements loop hides the operation in Python.

**How to verify:** Run pl.DataFrame({'values': [[1, 2], [3]]}).select(pl.col('values').list.eval(pl.element() * pl.element())) and assert the lists are [[1, 4], [9]].

**Expected:** The lists become [[1, 4],[9]].

## 6. Test null nested elements

Decide whether the collection is partially observed, invalid or imputable. Do not erase the distinction merely to simplify a numeric aggregation.

**Why it holds here:** A list like [1, None] says the collection exists but one member is unknown, which differs from both an empty list and a null list.

**Plausible wrong approach:** Applying drop_nulls inside the list before aggregating turns it into [1] and reports a complete basket of one.

**How to verify:** Count null elements with list.eval(pl.element().is_null()).list.sum() before aggregating, and check what list.sum returns for [1, None] on your installed version instead of assuming it.

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

Demonstrate empty, missing and repeated-element cases, then verify that any flattened table can still be related to its original records. This is essential for reliable event analytics and sequence-feature construction.
