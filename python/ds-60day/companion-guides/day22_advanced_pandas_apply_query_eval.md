# Day 22 — Advanced pandas: Vectorization, `query`, and Categoricals

**Level:** Intermediate

Express column operations with pandas/NumPy primitives before reaching for
row-wise `apply`. Then measure memory and performance on representative data.

## Learning objectives

By the end of this lesson, you can:

- replace common row-wise `apply(axis=1)` patterns with vectorized operations;
- use group `transform` when a group result must align with original rows;
- filter readable expressions with `query` and compute with `eval`;
- measure whether categorical dtype reduces memory for repeated strings;
- verify optimized output against a simple baseline.

## Prerequisites

Complete Day 21 (`python-21`) and Day 19 grouping (`python-19`).

## Vocabulary and mental model

- **Row-wise apply:** Python function called once per row; flexible but often
  slow.
- **Vectorized operation:** implementation acts on whole arrays/Series.
- **Expression engine:** machinery used by `query`/`eval` to evaluate column
  expressions.
- **Categorical:** integer codes plus a category lookup table.
- **Cardinality:** number of distinct values.
- **Memory profile:** measured bytes used by a representation.

Categoricals help when values repeat enough to outweigh the category table.
Near-unique strings can use the same or more memory.

## Worked example

```python
import pandas as pd

sales = pd.DataFrame(
    {"region": ["w", "w", "e"], "amount": [10.0, 30.0, 20.0]}
)
regional_total = sales.groupby("region")["amount"].transform("sum")
sales["regional_share"] = sales["amount"].div(regional_total)
large = sales.query("regional_share >= 0.5")
```

`transform` returns one aligned value per original row, so division is direct
and no row-wise lookup is required.

## Dataset note

The notebook uses Seaborn's cached `tips` data. A constructed DataFrame such as
the example above keeps this lesson fully offline.

## Exercises and progressive hints

1. Find a slow row-wise `apply` and replace it with vectorized logic. **Hint:**
   classify the operation as arithmetic, conditional selection, string method,
   mapping, or group transform; pandas has primitives for each.
2. Convert a repeated string column to categorical and profile memory. **Hint:**
   compare `memory_usage(deep=True)` before and after, record unique/row counts,
   and do not assume a high-cardinality column will improve.

### Additional mastery practice

Prefer vectorized operations and labeled expressions, but measure rather than assuming. Use categoricals only when repetition justifies them.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict why row-wise `apply(axis=1)` is usually slower than column arithmetic for a simple ratio.
   **Progressive hint:** Vectorized operations avoid constructing/calling Python work per row.
4. **Tracing:** Trace `frame.query('amount > @threshold')`: which name comes from a column and which comes from Python scope?
   **Progressive hint:** `@` marks an external Python variable.
5. **Implementation:** Write a function that compares memory before/after categorical conversion and keeps the category only when it reduces memory.
   **Progressive hint:** Use `memory_usage(deep=True)` on the Series.
6. **Debugging:** Replace a row-wise conditional `apply` with `np.select` or `.where` while preserving missing-value behavior.
   **Progressive hint:** List conditions from most specific to fallback.
7. **Edge case and explanation:** Explain why a nearly unique string ID can consume more memory as a category and why category levels must be handled during concatenation.
   **Progressive hint:** Categories store both codes and a level table.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- Why does group `transform` preserve row count while `agg` does not?
- When is `apply` still a reasonable choice?
- How do category count and row count affect memory savings?
- How do you refer to a Python variable safely inside `DataFrame.query`?

Expected behavior: vectorized and baseline outputs match (including missing
values), and the categorical decision is supported by measured bytes.

## Common pitfalls and diagnosis

- **Optimized results differ:** compare index, dtype, missing-value behavior,
  and boundary conditions before timing.
- **Division creates infinity:** handle zero group totals explicitly.
- **A `query` column name has spaces:** normalize names or quote with backticks.
- **Untrusted text is passed to `query`/`eval`:** do not treat user-provided
  expressions as safe code.
- **Categorical assignment rejects a new label:** add the category first or
  convert back to string.

## Continue

- [Open the learner notebook](../notebooks/day22_advanced_pandas_apply_query_eval.ipynb)
- [Check the separate solution](../solutions/day22_advanced_pandas_apply_query_eval/day22_solutions.md)
- [Next: Day 23 — Streaming data pipelines](day23_data_pipelines_generators.md)
