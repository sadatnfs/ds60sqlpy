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

2. Read `python/ds-60day/companion-guides/day19_pandas_groupby_pivot.md`, then open `python/ds-60day/notebooks/day19_pandas_groupby_pivot.ipynb` from the repository
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

**Lesson outcome:** use day 19 — groupby, aggregation, pivoting, and melting to practice split-apply-combine, grouped summaries, and reshaping
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

Grouped analysis starts with grain. `groupby` splits rows by key values,
applies reductions or transformations, and combines results. An
aggregation reduces each group and changes row grain; `transform`
returns one aligned value per original row and preserves row count.

A pivot makes combinations of keys into rows and columns while applying
an aggregation for duplicates. `melt` turns wide measurement columns
into a long variable/value pair. Reshaping changes representation, so
state which columns identify an observation and reconcile totals before
and after.

### Vocabulary in plain language

- **group key:** the column values defining membership in a group.
- **aggregation:** a reduction from many rows to a summary.
- **transform:** a group calculation aligned back to every original row.
- **pivot:** a reshape that places one key's values across columns.
- **melt:** a reshape from wide measurement columns to long rows.
- **grain:** what one output row represents after an operation.

### Syntax anatomy

`.groupby("region", as_index=False).agg(total=("amount", "sum"),
orders=("order_id", "nunique"))` names the group key, keeps it as a
column, and uses named aggregations whose left sides are output column
names. In `pivot_table`, `index` defines output rows, `columns` defines
output columns, `values` supplies measurements, and `aggfunc` resolves
duplicate combinations.

### Worked example 1 — Aggregate to one row per group

Write the output grain before reading the result. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [1, 2, 3, 4],
    "region": ["east", "east", "west", "west"],
    "amount": [10, 15, 7, 8],
})
summary = (
    orders.groupby("region", as_index=False)
    .agg(order_count=("order_id", "nunique"), total=("amount", "sum"))
)
summary.to_dict("records")
```

**Expected observation**

```text
`[{'region': 'east', 'order_count': 2, 'total': 25}, {'region': 'west', 'order_count': 2, 'total': 15}]`.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Align a group total back to every source row

Transform preserves the original index and row count. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
orders = orders.assign(
    region_total=orders.groupby("region")["amount"].transform("sum")
)
orders[["order_id", "region", "amount", "region_total"]].to_dict("records")
```

**Expected observation**

```text
Every east row receives `25` and every west row receives `15`; there are still four rows.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. State input and output grain before deciding between `agg` and `transform`.
2. Use named aggregations instead of accepting confusing MultiIndex columns.
3. Pass an explicit `aggfunc` and `fill_value` policy to `pivot_table`.
4. Reconcile additive totals and row counts across a reshape.

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

**Useful alternative:** Use `crosstab` for frequency tables, `pivot` only when combinations are unique, and `pivot_table` when duplicates need aggregation.

**Boundary to remember:** Missing group keys, unobserved categories, duplicate pivot cells, all-missing groups, and non-additive measures need explicit handling.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Group the lesson data by two categorical columns and compute named count, sum, mean, and median outputs. **Before code:** state the output grain and whether missing group keys are included. **Constraints:** use named `.agg`, avoid ambiguous MultiIndex columns, and distinguish row count from unique-entity count.
   **Verify:** assert group-key uniqueness and reconcile the summed additive measure to the input total.

2. Create a pivot table and then return it to long form with `melt` or `stack`. **Contract:** choose explicit index, column, value, aggregation, and missing-cell policy.
   **Expected behavior:** the long form clearly identifies every dimension and measurement.
   **Verify:** reconcile non-missing values/totals and explain any rows introduced or removed.

### Additional mastery practice

Write the input and output grain before grouping or reshaping. Reconcile row counts and totals at equivalent grains.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict whether rows with a missing group key are included by default and compare `dropna=True` with `dropna=False`.
   **Progressive hint:** Missing group keys are normally excluded unless requested.
   **Verify:** Group the same fixture both ways; assert totals differ exactly by the missing-key rows and state which output matches the intended policy.
4. **Tracing:** Trace a wide table through `melt` and back through `pivot_table`; name the identifier, variable, and value columns.
   **Progressive hint:** Reshaping changes layout, not the underlying measures.
   **Verify:** Assert the long table has identifier/variable/value columns and that pivoting back preserves the original labeled values and additive total.
5. **Implementation:** Implement grouped weighted means without using a simple mean of group means.
   **Progressive hint:** Aggregate weighted numerators and denominators at the same grain.
   **Verify:** For two groups, compute numerator and denominator explicitly and assert the grouped weighted means, including the chosen zero-weight behavior.
6. **Debugging:** Repair a calculation that joins a customer-level total back to line items and then sums it, multiplying totals by line count.
   **Progressive hint:** Do not re-aggregate a measure after broadcasting it to a finer grain.
   **Verify:** Show the inflated total after summing broadcast customer totals, then assert the repaired grain-aware calculation matches the original customer-level total.
7. **Edge case and explanation:** Handle groups whose total weight is zero and categories with no observed rows; state whether they appear in output.
   **Progressive hint:** Make zero-denominator and categorical `observed` behavior explicit.
   **Verify:** Test a zero-weight group and an unobserved categorical level; assert their value/presence follows the documented denominator and `observed` policy.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-19`
(Day 19 — GroupBy, Aggregation, Pivoting, and Melting). Direct catalog prerequisites: `python-18`.
I have completed the direct prerequisites: `python-18`. Emphasize split-apply-combine, grouped summaries, and reshaping.
Read `python/ds-60day/companion-guides/day19_pandas_groupby_pivot.md` and use the learner notebook
`python/ds-60day/notebooks/day19_pandas_groupby_pivot.ipynb`. Do not open or quote anything under `solutions/` unless
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
