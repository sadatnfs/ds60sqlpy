# Day 17 — pandas Series, DataFrames, and Indexing

**Level:** Intermediate

A DataFrame is a labeled table. Unlike a spreadsheet cell reference, a pandas
selection has a shape, dtype, index, and alignment behavior.

## Learning objectives

By the end of this lesson, you can:

- create and inspect a `Series` and `DataFrame`;
- select columns, rows, and scalar positions with `[]`, `.loc`, and `.iloc`;
- build and apply a boolean mask;
- set, sort, and reset an index;
- avoid ambiguous chained assignment.

## Prerequisites

Complete Day 16 (`python-16`): arrays, shapes, dtypes, masks, and vectorization.

## Vocabulary and mental model

- **Series:** one-dimensional labeled array.
- **DataFrame:** two-dimensional collection of aligned Series.
- **Index:** row labels used for selection and alignment; not necessarily a
  row-number sequence or unique identifier.
- **Label selection:** `.loc`; **position selection:** `.iloc`.
- **Boolean mask:** aligned true/false values selecting rows.
- **Alignment:** pandas combines labeled objects by index/column labels.

## Worked example

```python
import pandas as pd

sales = pd.DataFrame(
    {
        "region": ["west", "east", "west"],
        "amount": [12.0, 9.5, 15.0],
        "units": [2, 1, 3],
    }
)
west = sales.loc[sales["region"].eq("west"), ["amount", "units"]]
first_value = sales.iloc[0, 1]
```

This example is fully offline and deterministic. Inspect `.shape`, `.dtypes`,
`.head()`, and `.describe()` before transforming unfamiliar data.

## Dataset note

The notebook uses Seaborn's `tips` sample. `sns.load_dataset("tips")` downloads
it on the first uncached use and then reuses Seaborn's local cache. Run once
while online before an offline session, or practice the same operations with a
small constructed DataFrame like the one above.

## Exercises and progressive hints

1. Select Dinner rows and compute the average tip. **Hint:** create one boolean
   mask, select the `tip` Series, then aggregate.
2. Add `is_big_party` for rows where `size >= 5`. **Hint:** assign one
   vectorized comparison to a new column; do not loop through rows.
3. Sort descending by tip percentage (`tip / total_bill`). **Hint:** derive a
   named column first so you can inspect divide-by-zero or missing results.

## Self-check

- What determines whether `df["col"]` returns a Series or DataFrame?
- When should `.iloc` be used instead of `.loc`?
- How can two Series with different indexes produce missing values when added?
- Why is an index not automatically a database primary key?

Expected behavior: the Dinner calculation is a scalar, the new column is
boolean, and the highest valid tip percentage appears first.

## Common pitfalls and diagnosis

- **`KeyError` for an existing-looking label:** inspect exact column names,
  whitespace, capitalization, and index levels.
- **`SettingWithCopyWarning`:** combine row/column selection in one `.loc[...]`
  assignment or make an intentional `.copy()`.
- **Unexpected missing values after arithmetic:** inspect both indexes; pandas
  aligned labels rather than positions.
- **`df.info()` prints `None` afterward:** it prints its report and returns
  `None`; call it without wrapping in `print`.
- **A ratio is infinite:** detect zero denominators before sorting.

## Continue

- [Open the learner notebook](../notebooks/day17_pandas_intro.ipynb)
- [Check the separate solution](../solutions/day17_pandas_intro/day17_solutions.md)
- [Next: Day 18 — I/O and cleaning](day18_pandas_io_cleaning.md)
