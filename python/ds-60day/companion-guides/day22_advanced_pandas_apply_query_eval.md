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

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day22_advanced_pandas_apply_query_eval.md`, then open `python/ds-60day/notebooks/day22_advanced_pandas_apply_query_eval.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 22 — advanced pandas: vectorization, `query`, and categoricals to practice pandas vectorization, expression APIs, and memory-aware categoricals
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

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

### Worked example 1 — Replace row-wise conditional logic with masks

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

**Expected observation**

```text
`[{'amount': 5, 'band': 'low'}, {'amount': 20, 'band': 'medium'}, {'amount': 60, 'band': 'high'}]`.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Measure categorical conversion

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

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Classify row-wise logic as arithmetic, condition, string, mapping, or group transform before accepting `apply`.
2. List conditions from most specific to fallback and test missing values separately.
3. In `query`, distinguish column names from `@` external variables.
4. Measure categorical memory deeply and review category alignment before concatenation.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

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
   **Verify:** Set a known threshold and assert the selected row indexes; change only the Python variable and confirm `@threshold`—not a column—controls the result.
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

## Continue

- [Open the learner notebook](../notebooks/day22_advanced_pandas_apply_query_eval.ipynb)
- [Check the separate solution](../solutions/day22_advanced_pandas_apply_query_eval/day22_solutions.md)
- [Next: Day 23 — Streaming data pipelines](day23_data_pipelines_generators.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-22`
(Day 22 — Advanced pandas: Vectorization, `query`, and Categoricals). Direct catalog prerequisites: `python-21`.
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
