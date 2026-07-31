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

2. Read `python/ds-60day/companion-guides/day17_pandas_intro.md`, then open `python/ds-60day/notebooks/day17_pandas_intro.ipynb` from the repository
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

**Lesson outcome:** use day 17 — pandas series, dataframes, and indexing to practice labeled tabular data, row grain, indexes, selection, and vectorized columns
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A Series is a one-dimensional labeled array; a DataFrame is a table of
labeled columns sharing an index. Before manipulating a DataFrame,
state its **row grain**—what one row represents—and what makes a row
unique. Column names carry variable meaning; the index carries row
labels, which may or may not be a business key.

`loc` selects by labels and boolean masks; `iloc` selects by integer
positions. Pandas aligns many operations by index labels rather than
blindly by current row position. Prefer vectorized column operations
and explicit `.loc` assignment. Inspect shape, dtypes, missingness, and
a small sample before trusting a calculation.

### Vocabulary in plain language

- **Series:** a one-dimensional array with an index and optional name.
- **DataFrame:** a two-dimensional collection of aligned labeled columns.
- **index:** the labels identifying rows for selection and alignment.
- **row grain:** the real-world meaning of one row.
- **boolean mask:** a True/False Series used to select matching rows.
- **vectorized operation:** a column/array operation applied without an explicit Python row loop.

### Syntax anatomy

`frame.loc[mask, ["name", "score"]]` has two selectors: rows before the
comma and columns after it. `frame.iloc[:3, 0]` uses positions instead
of labels. `frame["rate"] = frame["part"] / frame["whole"]` aligns the
two Series by index and assigns the computed Series under a new column
label.

### Worked example 1 — Build and inspect a tiny labeled table

Use constructed data so the example is fully offline. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import pandas as pd

sales = pd.DataFrame({
    "order_id": [101, 102, 103],
    "region": ["west", "east", "west"],
    "amount": [20.0, 35.0, 15.0],
})
(sales.shape, sales.dtypes.astype(str).to_dict(), sales["order_id"].is_unique)
```

**Expected observation**

```text
`((3, 3), {...}, True)`. The dtype spellings may vary slightly; each row represents one order and `order_id` is unique here.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Filter rows and derive a column without a loop

A mask selects west orders; a vectorized expression creates tax. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
west = sales.loc[sales["region"].eq("west"), ["order_id", "amount"]]
sales = sales.assign(amount_with_tax=sales["amount"] * 1.08)
(west["order_id"].tolist(), sales["amount_with_tax"].round(2).tolist())
```

**Expected observation**

```text
`([101, 103], [21.6, 37.8, 16.2])`. The original row index is retained in `west`.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Print shape, column names, dtypes, and row grain before writing a selection.
2. Use `.loc` for labels/masks and `.iloc` for positions; never infer from integer-looking labels.
3. Check mask index alignment when a correct-looking mask selects the wrong rows or raises.
4. Use `.copy()` for an intentionally independent filtered frame and `.loc` for explicit assignment.

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

**Useful alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Boundary to remember:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Using the lesson DataFrame, select rows where `time == 'Dinner'`, then compute the mean of the selected `tip` values. **Before code:** state the row grain and write the mask separately.
   **Expected behavior:** the result is one scalar equal to `dinner_rows['tip'].mean()`. **Constraints:** use `.loc` and do not loop.
   **Verify:** assert every selected row is Dinner and the selection is non-empty before reporting the mean.

2. Add a Boolean `is_big_party` column that is `True` exactly when `size >= 5`. **Constraints:** use one vectorized comparison and explicit assignment; do not use row-wise `apply`.
   **Verify:** compare the new column with `df['size'].ge(5)`, inspect both True and False rows, and confirm row count/index are unchanged.

3. Create a safe `tip_rate = tip / total_bill`, treating a zero bill as missing rather than infinity, then sort descending by `tip_rate`. **Constraints:** preserve the unsorted source in a separate name and choose where missing rates appear.
   **Verify:** assert there are no infinite values and that non-missing rates are monotonically decreasing.

### Additional mastery practice

State a DataFrame's row grain, column meanings, and index role before selecting or deriving data. Prefer vectorized, explicit assignments.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict the difference between `.loc[labels]` and `.iloc[positions]` after an integer index has been reordered.
   **Progressive hint:** Labels are not automatically row positions.
   **Verify:** After reordering integer labels, assert `.loc` returns the requested labels and `.iloc` returns the requested positions; list both resulting indexes.
5. **Tracing:** Trace a boolean mask through creation, alignment by index, and row selection. What happens if mask/index labels differ?
   **Progressive hint:** Pandas aligns many labeled objects by index.
   **Verify:** Display mask and frame indexes side by side, then assert aligned selection for matching labels and the documented error/reindex policy for mismatches.
6. **Implementation:** Create a safe `tip_rate` column that yields missing values rather than infinity when `total_bill` is zero.
   **Progressive hint:** Mask or replace the zero denominator before division.
   **Verify:** Assert zero bills yield missing rates, positive bills yield the calculated ratio, and the entire column contains no positive/negative infinity.
7. **Debugging:** Repair chained assignment on a filtered DataFrame and explain when to use `.loc` or an explicit `.copy()`.
   **Progressive hint:** Make ownership and target rows explicit.
   **Verify:** Turn chained-assignment warnings into explicit `.loc` or `.copy()` ownership; assert the intended frame changes and the unintended frame does not.
8. **Edge case and explanation:** Compute a statistic for a possibly empty selection and return `None` instead of silently presenting `NaN` as a real result.
   **Progressive hint:** Check `.empty` before aggregating when absence has business meaning.
   **Verify:** Test nonempty and empty selections; assert the former returns the statistic and the latter returns `None`, not a value presented as meaningful.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-17`
(Day 17 — pandas Series, DataFrames, and Indexing). Direct catalog prerequisites: `python-16`.
I have completed the direct prerequisites: `python-16`. Emphasize labeled tabular data, row grain, indexes, selection, and vectorized columns.
Read `python/ds-60day/companion-guides/day17_pandas_intro.md` and use the learner notebook
`python/ds-60day/notebooks/day17_pandas_intro.ipynb`. Do not open or quote anything under `solutions/` unless
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
