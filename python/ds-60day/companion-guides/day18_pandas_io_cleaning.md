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

1. Load CSV with a parsed date column and make it the index. **Hint:** inspect
   invalid dates before setting the index; `errors="coerce"` turns them into
   `NaT`.
2. Impute numeric columns with their median and categorical columns with their
   mode. **Hint:** select columns by dtype and define behavior for an all-missing
   column whose mode is empty.
3. Write `clean(df)` returning a fully typed DataFrame. **Hint:** copy first,
   normalize names/values, convert types, then assert the output contract.

### Additional mastery practice

Profile before cleaning, preserve raw input, and make every conversion, imputation, and rejection rule observable and testable.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict the results of `pd.to_datetime(..., errors='coerce', utc=True)` for valid text, invalid text, and a timestamp with an offset.
   **Progressive hint:** Invalid text becomes `NaT`; valid values normalize to UTC.
5. **Tracing:** Trace conversion from object strings to pandas nullable `Int64`, including an empty value.
   **Progressive hint:** Nullable integer dtype can represent `<NA>` without becoming float.
6. **Implementation:** Implement a cleaner that normalizes column names, parses an event time, converts quantity, and returns a copy plus a quality summary.
   **Progressive hint:** Record invalid counts before dropping or imputing anything.
7. **Debugging:** Repair an in-place operation performed on a chained selection.
   **Progressive hint:** Use assignment on the owned copy and avoid `inplace=True` on a temporary object.
8. **Edge case and explanation:** Choose behavior for an all-missing numeric column whose median is also missing. Reject, use a domain default, or preserve missing—and justify.
   **Progressive hint:** A statistical fallback cannot be computed from zero observations.

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
