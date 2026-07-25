# Day 19 — GroupBy, Aggregation, Pivoting, and Melting

**Level:** Intermediate

Grouping changes a table's grain. State the output grain before writing the
aggregation so row counts and totals can be checked.

## Learning objectives

By the end of this lesson, you can:

- apply the split-apply-combine model with `groupby`;
- create named aggregations at a stated grain;
- distinguish `.agg` from `.transform`;
- reshape long data to wide with `pivot_table`;
- reshape wide data to long with `melt` and validate totals.

## Prerequisites

Complete Day 18 (`python-18`): typed, cleaned DataFrames and missing-value rules.

## Vocabulary and mental model

- **Grain:** what one row represents.
- **Group key:** columns defining each output group.
- **Aggregation:** many values reduced to one value per group.
- **Transform:** group calculation broadcast back to original rows.
- **Long format:** observations in rows; **wide format:** categories spread
  across columns.
- **Pivot table:** aggregation plus reshape; duplicate coordinates are combined.

## Worked example

```python
import pandas as pd

sales = pd.DataFrame(
    {
        "region": ["west", "west", "east"],
        "channel": ["web", "store", "web"],
        "amount": [10.0, 20.0, 15.0],
    }
)
summary = (
    sales.groupby(["region", "channel"], observed=True)
    .agg(total_amount=("amount", "sum"), rows=("amount", "size"))
    .reset_index()
)
```

The result has one row per `(region, channel)`. `size` counts rows, while
`count` would exclude missing values in the selected column.

## Dataset note

The notebook uses Seaborn's cached `tips` data. The constructed example above
is the offline alternative when that cache has not been primed.

## Exercises and progressive hints

1. Compute total revenue and average tip by `(day, smoker)`. **Hint:** write the
   intended output column names and source-column/function pairs before calling
   `.agg`.
2. Create a pivot table of average tip by day and time, filling absent
   combinations with zero. **Hint:** identify the row index, output columns,
   measured value, and aggregation independently.
3. Melt a wide table to long, then group to verify totals against the original.
   **Hint:** preserve an identifier column and compare at the same grain, using
   a tolerance for floating-point results.

## Self-check

- How does `.transform("sum")` differ in shape from `.agg("sum")`?
- Why can `pivot` fail where `pivot_table` succeeds?
- What does one row represent before and after your groupby?
- When is filling a missing combination with zero semantically wrong?

Expected behavior: group output has unique keys, the pivot has predictable
labels, and a round-trip validation reconciles totals.

## Common pitfalls and diagnosis

- **Totals are too small:** `count` ignored missing measurements; compare with
  `size`.
- **Categories disappear:** check missing group keys and pandas categorical
  `observed` behavior.
- **Unexpected MultiIndex columns:** use named aggregations or flatten labels
  deliberately.
- **Pivot output has a surprising order:** reindex explicitly rather than
  relying on display order.
- **Melted totals differ:** verify identifier/value columns and compare equal
  grains, not an average of averages.

## Continue

- [Open the learner notebook](../notebooks/day19_pandas_groupby_pivot.ipynb)
- [Check the separate solution](../solutions/day19_pandas_groupby_pivot/day19_solutions.md)
- [Next: Day 20 — Merging and joins](day20_pandas_merging_joins.md)
