# Day 22: Advanced pandas: Vectorization, query, and Categoricals

**Offline teaching data:** the `restaurant-bills` [synthetic fixture](../../fixtures/README.md) is invented, so its numbers prove methods, not facts.


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

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Open `python-22` in the classroom, or `python/ds-60day/notebooks/day22_advanced_pandas_apply_query_eval.ipynb` on a host; the [Python study guide](../../STUDY-GUIDE.md) explains both.

**Outcome:** Replace row-wise apply with vectorized code, query, and categoricals.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive: build the idea before the syntax

### Start with one mental picture

Pandas is fastest and clearest when an operation can be expressed over
entire columns: arithmetic, comparisons, string/datetime accessors,
mapping, masks, or group transforms. A row-wise `apply(axis=1)` builds a
Series and calls Python for each row, so it should be a last resort for
genuinely row-dependent logic, not a default.

`query` and `eval` provide readable expression syntax but introduce
another name-resolution layer. Categoricals store repeated labels as
integer codes plus a level table; they can reduce memory and encode a
closed vocabulary, but nearly unique values may use more memory. Measure
before and after and define behavior for unseen categories.

### Vocabulary in plain language

- **vectorization:** column/array operations executed without a Python call per row.
- **row-wise apply:** calling a Python function with each row Series.
- **expression:** a calculation/filter written for `query` or `eval`.
- **categorical:** codes plus a finite table of allowed label values.
- **cardinality:** the count of distinct values in a column.
- **memory profiling:** measuring retained memory under a stated representation.

### Syntax anatomy

`frame.query("amount > @threshold")` resolves `amount` as a column and
`@threshold` from Python scope. `frame.eval("rate = part / whole")` can
assign an expression result. `series.astype("category")` creates codes
and categories; `memory_usage(deep=True)` includes referenced string
storage for a more honest comparison.

### Worked example 1: Replace row-wise conditional logic with masks

Column expressions state each rule and preserve index alignment. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import numpy as np
import pandas as pd

frame = pd.DataFrame({"amount": [5, 20, 60]})
frame["band"] = np.select(
    [frame["amount"].ge(50), frame["amount"].ge(10)],
    ["high", "medium"],
    default="low",
)
frame.to_dict("records")
```

**Expected observation:** `[{'amount': 5, 'band': 'low'}, {'amount': 20, 'band': 'medium'}, {'amount': 60, 'band': 'high'}]`.

### Worked example 2: Measure categorical conversion

Keep the conversion only when data characteristics justify it. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
labels = pd.Series(["east", "west"] * 1_000, name="region")
categorical = labels.astype("category")
{
    "unique": labels.nunique(),
    "rows": len(labels),
    "object_bytes": int(labels.memory_usage(deep=True)),
    "category_bytes": int(categorical.memory_usage(deep=True)),
}
```

**Expected observation**

```text
Two unique labels across 2,000 rows are reported, and the categorical representation is normally smaller. Exact byte counts vary by pandas version.
```

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Classify row-wise logic as arithmetic, condition, string, mapping, or group transform before accepting `apply`.
2. List conditions from most specific to fallback and test missing values separately.
3. In `query`, distinguish column names from `@` external variables.
4. Measure categorical memory deeply and review category alignment before concatenation.

### Practice ramp

Work this lesson's exercises in the five practice modes from the [Python study guide](../../STUDY-GUIDE.md).

**Useful alternative:** A named Python function plus `apply` is acceptable for truly irregular per-row objects; benchmark and keep the contract explicit.

**Boundary to remember:** Missing values in conditions, divide-by-zero, nearly unique strings, unseen category levels, and unsafe dynamic expressions require care.
<!-- END BEGINNER DEEP DIVE -->

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

sales = pd.DataFrame({"region": ["w", "w", "e"], "amount": [10.0, 30.0, 20.0]})
regional_total = sales.groupby("region")["amount"].transform("sum")
sales["regional_share"] = sales["amount"].div(regional_total)
large = sales.query("regional_share >= 0.5")
```

`transform` returns one aligned value per original row, so division is direct
and no row-wise lookup is required.

### Measure apply against vectorized code, then use eval

Claims about speed need a measurement on the same data. The example computes
one tip rate per row three ways: a row-wise `apply`, plain column arithmetic,
and `DataFrame.eval`, which evaluates a string expression over columns. It
checks that all three agree before comparing the two timings.

```python
import time

import numpy as np
import pandas as pd

rng = np.random.default_rng(22)
bills = pd.DataFrame({"tip": rng.uniform(1, 10, 20_000), "total_bill": rng.uniform(10, 60, 20_000)})

start = time.perf_counter()
by_row = bills.apply(lambda row: row["tip"] / row["total_bill"], axis=1)
apply_seconds = time.perf_counter() - start

start = time.perf_counter()
vectorized = bills["tip"] / bills["total_bill"]
vectorized_seconds = time.perf_counter() - start

with_eval = bills.eval("tip / total_bill")
(
    bool(np.allclose(by_row, vectorized)),
    bool(np.allclose(with_eval, vectorized)),
    apply_seconds > 10 * vectorized_seconds,
)
```

**Expected observation:** `(True, True, True)`: the three results agree, and
the row-wise `apply` takes more than ten times as long as column arithmetic (on
the machine used to write this lesson it was roughly 200 to 400 times slower;
exact timings vary from run to run). `eval` gave the same numbers, but it is
not automatically faster: for small frames, parsing the expression costs more
than the arithmetic itself, and the pandas documentation recommends it mainly
for large frames. Use `eval` and `query` for readable column expressions, and
time any speed claim on representative data.

## Dataset note

The notebook uses the original synthetic restaurant-bills fixture. A constructed DataFrame such as
the example above keeps this lesson fully offline.

## Exercises and progressive hints

1. Find one row-wise `apply(axis=1)` in a supplied example and replace it with column arithmetic, string methods, mapping, masks, `np.select`, or group transform as appropriate.
   **Expected behavior:** values and index match the original for normal and missing inputs. **Constraints:** do not optimize by changing the contract.
   **Verify:** use `pd.testing` to assert equal values, dtype, and index, then report repeated median execution seconds for both implementations on the same representative frame.

2. Convert a repeated string column to categorical only after profiling. **Evidence:** record row count, unique count, object memory, categorical memory, and the category levels.
   **Expected behavior:** keep the categorical version only if it reduces memory for this data.
   **Verify:** values remain equivalent and explain why a nearly unique ID may become larger.

### Additional mastery practice

Prefer vectorized operations and labeled expressions, but measure rather than assuming. Use categoricals only when repetition justifies them.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict why row-wise `apply(axis=1)` is usually slower than column arithmetic for a simple ratio.
   **Progressive hint:** Vectorized operations avoid constructing/calling Python work per row.
   **Verify:** Assert row-wise and vectorized ratios agree including missing values, then report repeated timings on the same frame rather than a single anecdote.
4. **Tracing:** Trace `frame.query('amount > @threshold')`: which name comes from a column and which comes from Python scope?
   **Progressive hint:** `@` marks an external Python variable.
   **Verify:** Set a known threshold and assert the selected row indexes; change only the Python variable and confirm `@threshold`, not a column, controls the result.
5. **Implementation:** Write a function that compares memory before/after categorical conversion and keeps the category only when it reduces memory.
   **Progressive hint:** Use `memory_usage(deep=True)` on the Series.
   **Verify:** Assert values are unchanged, record both deep-memory counts, and return categorical only in the fixture where its bytes are smaller.
6. **Debugging:** Replace a row-wise conditional `apply` with `np.select` or `.where` while preserving missing-value behavior.
   **Progressive hint:** List conditions from most specific to fallback.
   **Verify:** Use rows covering every condition plus missing input; assert vectorized labels match the reference apply and missing policy exactly.
7. **Edge case and explanation:** Explain why a nearly unique string ID can consume more memory as a category and why category levels must be handled during concatenation.
   **Progressive hint:** Categories store both codes and a level table.
   **Verify:** Profile a repeated label and a nearly unique ID; assert the measured memory directions and reconcile category levels before/after concatenation.

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
- **Memory numbers change under pandas 3:** pandas 3 stores text in the `str`
  dtype instead of `object` (see the pandas 3 note in Day 17), which changes
  the baseline for a categorical memory comparison. Measure with
  `memory_usage(deep=True)` on the version you actually run.

## Continue

- [Open the learner notebook](../notebooks/day22_advanced_pandas_apply_query_eval.ipynb)
- [Check the separate solution](../solutions/day22_advanced_pandas_apply_query_eval/day22_solutions.md)
- [Next: Day 23; Streaming data pipelines](day23_data_pipelines_generators.md)

## Ask an AI tutor about this lesson

AI coaching is optional. To use a tutor, copy this prompt from the repository root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-22`
(Day 22: Advanced pandas: Vectorization, `query`, and Categoricals). Direct catalog prerequisites: `python-21`.
I have completed the direct prerequisites: `python-21`. Emphasize pandas vectorization, expression APIs, and memory-aware categoricals.
Read `python/ds-60day/companion-guides/day22_advanced_pandas_apply_query_eval.md` and use the learner notebook
`python/ds-60day/notebooks/day22_advanced_pandas_apply_query_eval.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
