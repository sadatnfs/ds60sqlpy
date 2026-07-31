# Day 18 — pandas I/O and Data Cleaning

**Level:** Intermediate

Cleaning is a documented conversion from messy input to a predictable table.
Never hide destructive assumptions inside a long notebook cell.

## Learning objectives

By the end of this lesson, you can:

- load CSV or JSON while making parsing assumptions explicit;
- measure missingness before choosing drop or imputation rules;
- convert numeric and datetime fields with diagnosable invalid values;
- write a non-mutating `clean(frame)` function and use `.pipe`;
- verify resulting dtypes and required fields.

## Prerequisites

Complete Day 17 (`python-17`): DataFrames, selection, dtypes, and copies.





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

2. Read `python/ds-60day/companion-guides/day18_pandas_io_cleaning.md`, then open `python/ds-60day/notebooks/day18_pandas_io_cleaning.ipynb` from the repository
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

**Lesson outcome:** use day 18 — pandas i/o and data cleaning to practice pandas input boundaries, explicit cleaning, and reproducible output
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

Reading a file creates a DataFrame but does not prove its schema.
External columns may have missing values, inconsistent spellings,
numeric text, impossible values, or duplicate records. Profile those
conditions before converting types, because conversion can hide which
representations arrived.

A cleaning function should accept a raw frame, work on a copy, apply
named deterministic steps, and return a clean frame. Record why rows or
values change. Prefer nullable pandas dtypes where absence is valid, and
make the function idempotent when practical: cleaning already-clean
data should not keep changing it.

### Vocabulary in plain language

- **missing value:** an absent observation represented by pandas missing markers.
- **dtype:** a column's stored representation and operation rules.
- **coercion:** conversion that may replace unparseable values with missing data.
- **duplicate:** a repeated row or repeated key under a stated definition.
- **idempotent:** producing the same result when applied again to its own output.
- **data lineage:** evidence about where data came from and how it changed.

### Syntax anatomy

`pd.to_numeric(series, errors="coerce")` converts compatible text and
marks failures missing; those new missing values must be counted and
reviewed. `.assign(...)` returns a new frame with derived/replaced
columns. `.pipe(clean_step)` passes a DataFrame into a named function,
making a sequence of transformations readable.

### Worked example 1 — Normalize text and numeric representations

Count conversion failures instead of silently losing them. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import pandas as pd

raw = pd.DataFrame({
    "name": [" Ada ", "Lin", "Grace"],
    "score": ["10", "missing", "8.5"],
})
clean_scores = pd.to_numeric(raw["score"], errors="coerce")
cleaned = raw.assign(
    name=raw["name"].str.strip(),
    score=clean_scores,
)
(cleaned.to_dict("records"), int(cleaned["score"].isna().sum()))
```

**Expected observation**

```text
The names are trimmed, numeric text is converted, and one conversion failure is reported as missing.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Write a cleaning function that preserves raw input

Copy at the boundary and make repeated application stable. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def clean_people(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["name"] = result["name"].str.strip()
    result["score"] = pd.to_numeric(result["score"], errors="coerce")
    return result.drop_duplicates().reset_index(drop=True)

once = clean_people(raw)
twice = clean_people(once)
(raw.loc[0, "name"], once.equals(twice))
```

**Expected observation**

```text
`(' Ada ', True)`. The raw frame is unchanged and the demonstrated cleaner is idempotent on this data.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Profile raw dtypes, missing counts, unique spellings, and duplicate keys before cleaning.
2. After coercion, count values that became missing and retain examples for review.
3. Avoid `inplace=True` while learning; returned frames make ownership and chaining clearer.
4. Re-read saved output and reconcile row count, schema, and key totals with the in-memory clean frame.

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

**Useful alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Boundary to remember:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Missing value:** absent/unknown observation, commonly represented by
  `NaN`, `NaT`, or `pd.NA`.
- **Imputation:** replace missing values using an explicit rule.
- **Coercion:** convert incompatible values to a sentinel such as `NaN`.
- **Idempotent cleaning:** applying the cleaner twice produces the same result.
- **Data contract:** expected columns, types, ranges, and missingness.
- **Pipeline:** ordered transformations with named responsibilities.

## Worked example

```python
import pandas as pd

raw = pd.DataFrame(
    {"amount": ["10.5", "bad", None], "city": [" SF ", "ny", "NY"]}
)


def clean(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["amount"] = pd.to_numeric(result["amount"], errors="coerce")
    result["city"] = result["city"].str.strip().str.upper().astype("string")
    return result


tidy = raw.pipe(clean)
```

Inspect the rows that became missing before filling or dropping them; coercion
without review can hide a source-system change.

## Dataset and format notes

The notebook's Titanic sample follows the same Seaborn first-use download/cache
behavior described on Day 17. CSV and JSON work with course defaults. Parquet
requires a compatible optional engine; do not assume a fresh environment has
one unless the project declares and installs it.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Load a local CSV into pandas, recording path, encoding, row grain, shape, columns, dtypes, missing counts, and duplicate-key counts before changing anything.
   **Expected behavior:** produce a compact profile, not a full data dump. **Constraint:** use repository-relative `Path` objects and no network source.
   **Verify:** restart the kernel and reproduce the same profile.

2. Implement `clean_frame(raw)` that trims selected text, converts documented numeric/date fields, handles missing values by written policy, resolves duplicates by a stated key, and returns a new DataFrame. **Constraints:** do not mutate `raw` or use broad `dropna`; record conversion failures.
   **Verify:** assert raw preservation and `clean_frame(clean_frame(raw)).equals(clean_frame(raw))` for this contract.

3. Save only the cleaned frame under an ignored learner artifact directory, then read it back.
   **Expected behavior:** reloaded row count, columns, and key totals match the in-memory clean frame. **Constraints:** create parent folders with `Path.mkdir`, avoid absolute paths, and do not overwrite raw input.
   **Verify:** Read the saved file back and assert row count, ordered columns, dtypes/normalization policy, and selected key totals match the cleaned in-memory frame.

### Additional mastery practice

Profile before cleaning, preserve raw input, and make every conversion, imputation, and rejection rule observable and testable.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict the results of `pd.to_datetime(..., errors='coerce', utc=True)` for valid text, invalid text, and a timestamp with an offset.
   **Progressive hint:** Invalid text becomes `NaT`; valid values normalize to UTC.
   **Verify:** Create three input rows and assert valid/offset timestamps normalize to the expected UTC instants while invalid text becomes `NaT` and is counted.
5. **Tracing:** Trace conversion from object strings to pandas nullable `Int64`, including an empty value.
   **Progressive hint:** Nullable integer dtype can represent `<NA>` without becoming float.
   **Verify:** Record value and dtype before/after conversion; assert numeric strings become integers, empty input becomes `<NA>`, and dtype is nullable `Int64`.
6. **Implementation:** Implement a cleaner that normalizes column names, parses an event time, converts quantity, and returns a copy plus a quality summary.
   **Progressive hint:** Record invalid counts before dropping or imputing anything.
   **Verify:** Assert the cleaner leaves raw unchanged, returns expected normalized columns/dtypes, and reports exact invalid timestamp/quantity counts.
7. **Debugging:** Repair an in-place operation performed on a chained selection.
   **Progressive hint:** Use assignment on the owned copy and avoid `inplace=True` on a temporary object.
   **Verify:** Reproduce the warning/failure, then assert explicit owned-copy assignment changes only the intended frame and uses no `inplace` temporary mutation.
8. **Edge case and explanation:** Choose behavior for an all-missing numeric column whose median is also missing. Reject, use a domain default, or preserve missing—and justify.
   **Progressive hint:** A statistical fallback cannot be computed from zero observations.
   **Verify:** Run an all-missing fixture and assert the exact chosen reject/default/preserve policy; document why no sample median was available.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- Why should missingness be measured by column and important segment?
- What information can `errors="coerce"` discard?
- Why should a cleaner return a new DataFrame?
- How would you test that cleaning is idempotent?

Expected behavior: dates are real datetimes, imputation leaves no targeted
missing values, and the input frame remains unchanged.

## Common pitfalls and diagnosis

- **Dates parse with the wrong day/month order:** specify a format when known
  and test an unambiguous fixture.
- **Median imputation changes an integer dtype:** choose pandas' nullable dtypes
  or document the float result.
- **Mode access raises `IndexError`:** the column is empty/all-missing; define a
  fallback or reject the data.
- **A cleaner changes its input:** add a test comparing the original fixture
  before and after the call.
- **CSV values gain unexpected types:** inspect raw strings and pass explicit
  `dtype`/parsing rules at the boundary.

## Continue

- [Open the learner notebook](../notebooks/day18_pandas_io_cleaning.ipynb)
- [Check the separate solution](../solutions/day18_pandas_io_cleaning/day18_solutions.md)
- [Next: Day 19 — Grouping and reshaping](day19_pandas_groupby_pivot.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-18`
(Day 18 — pandas I/O and Data Cleaning). I am a complete beginner. Emphasize pandas input boundaries, explicit cleaning, and reproducible output.
Read `python/ds-60day/companion-guides/day18_pandas_io_cleaning.md` and use the learner notebook
`python/ds-60day/notebooks/day18_pandas_io_cleaning.ipynb`. Do not open or quote anything under `solutions/` unless
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
