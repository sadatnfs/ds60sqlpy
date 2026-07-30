# Day 20 — Merging and Joins

**Level:** Intermediate

A join combines tables according to keys and cardinality. Predict which rows
should survive and how many rows can be produced before calling `merge`.

## Learning objectives

By the end of this lesson, you can:

- choose inner, left, right, or outer join semantics;
- distinguish row concatenation from key-based merging;
- state and enforce one-to-one, one-to-many, or many-to-many cardinality;
- diagnose orphan keys, duplicate keys, dtype mismatches, and suffixes;
- reconcile row counts and totals after a merge.

## Prerequisites

Complete Day 19 (`python-19`): table grain, grouping keys, and aggregation.

## Vocabulary and mental model

- **Join key:** column(s) used to match rows.
- **Cardinality:** number of rows per key on each side (`1:1`, `1:m`, `m:1`,
  or `m:m`).
- **Inner join:** matched keys only; **left join:** every left row; **right
  join:** every right row; **outer join:** every key from either side.
- **Orphan:** row whose key has no match in the other table.
- **Row explosion:** unintended multiplication caused by duplicate keys.

## Worked example

```python
import pandas as pd

products = pd.DataFrame({"sku": ["A", "B"], "price": [4.0, 7.5]})
items = pd.DataFrame({"order_id": [1, 1, 2], "sku": ["A", "B", "A"]})

priced = items.merge(
    products,
    on="sku",
    how="left",
    validate="many_to_one",
    indicator=True,
)
assert priced["_merge"].eq("both").all()
```

The contract says many item rows may refer to one product row. `indicator=True`
makes missing matches visible during validation.

## Exercises and progressive hints

1. Join products, order items, and customers to compute revenue per customer.
   **Hint:** write each table's grain and key uniqueness first; calculate
   line-level revenue only after price and quantity share a row.
2. Demonstrate a right join and explain when it is useful. **Hint:** identify
   which right-side rows must survive; compare with swapping the inputs and
   performing a left join.
3. Use `validate="one_to_many"` to catch unexpected duplicates. **Hint:** place
   the table expected to have one row per key on the left, then deliberately
   duplicate one of its keys to observe the error.

### Additional mastery practice

Declare each table's grain and key cardinality before merging. Use validation and reconciliation to make row loss or multiplication visible.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** One key appears twice on the left and three times on the right. Predict the number of joined rows for that key.
   **Progressive hint:** A many-to-many match forms every pair: left count × right count.
5. **Tracing:** Trace an outer merge with `indicator=True` and classify `left_only`, `right_only`, and `both` rows.
   **Progressive hint:** The indicator is a compact reconciliation tool.
6. **Implementation:** Implement an anti-join returning left rows whose key has no right match.
   **Progressive hint:** Use a left merge with indicator, then filter `left_only`.
7. **Debugging:** Repair a merge whose `validate='one_to_many'` is reversed relative to the actual product-to-order-item relationship.
   **Progressive hint:** Say which side must have unique keys before choosing `1:m` or `m:1`.
8. **Edge case and explanation:** Investigate how missing keys match in pandas and decide whether to reject, sentinel-fill, or separate them before a business-key join.
   **Progressive hint:** Do not assume pandas null-key behavior matches SQL.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- How many output rows can an `m:m` match create for one key?
- Why might a left join produce more rows than the left input?
- What does an outer join reveal about data quality?
- Why should join-key dtypes be normalized before merging?

Expected behavior: revenue reconciles with line items, orphan rows are
identified rather than silently lost, and incorrect cardinality raises
`MergeError`.

## Common pitfalls and diagnosis

- **Row count unexpectedly multiplies:** measure duplicate counts on both key
  sets and add `validate`.
- **Matches are missing:** compare key dtypes, whitespace, case, and nulls.
- **`_x`/`_y` columns are confusing:** select needed columns or supply meaningful
  suffixes before downstream work.
- **Totals change after a join:** reconcile at the pre-join grain and inspect
  duplicated matches.
- **`concat` was used for a relational join:** use `merge`; `concat` stacks or
  aligns along an axis rather than matching business keys.

## Continue

- [Open the learner notebook](../notebooks/day20_pandas_merging_joins.ipynb)
- [Check the separate solution](../solutions/day20_pandas_merging_joins/day20_solutions.md)
- [Next: Day 21 — Time series with pandas](day21_time_series_pandas.md)
