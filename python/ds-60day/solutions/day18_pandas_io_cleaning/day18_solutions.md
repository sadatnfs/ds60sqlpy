# Day 18 — Solutions: Pandas I/O and Cleaning

We load data with types/dates, impute missing values, and return a fully typed DataFrame.

Contents
- Exercise 1: Read CSV with parse_dates and set as index
- Exercise 2: Impute numerics with median, categoricals with mode
- Exercise 3: clean(df) returning typed DataFrame

---

Exercise 1 — Read CSV with parse_dates
```python
import pandas as pd

df = pd.read_csv('sales.csv', parse_dates=['order_date'])
df = df.set_index('order_date').sort_index()
```

Exercise 2 — Impute missing values
```python
import numpy as np

num_cols = df.select_dtypes(include=['number']).columns
cat_cols = df.select_dtypes(include=['object','category']).columns

for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')
    df[c] = df[c].fillna(df[c].median())

for c in cat_cols:
    mode = df[c].mode(dropna=True)
    df[c] = df[c].fillna(mode.iat[0] if not mode.empty else '')
```

Exercise 3 — clean(df) with dtypes
```python
from typing import Mapping

def clean(df: pd.DataFrame, dtypes: Mapping[str, str] | None = None) -> pd.DataFrame:
    d = df.copy()
    # Standardize columns and types
    d = d.rename(columns=str.lower)
    if dtypes:
        for col, typ in dtypes.items():
            if col in d:
                d[col] = d[col].astype(typ)
    # Coerce numeric-like strings
    for c in d.columns:
        if d[c].dtype == 'object':
            # try numeric then datetime; keep object if both fail
            d_num = pd.to_numeric(d[c], errors='ignore')
            if d_num.dtype != 'object':
                d[c] = d_num
                continue
            d_dt = pd.to_datetime(d[c], errors='ignore', utc=True)
            if hasattr(d_dt, 'dt'):
                d[c] = d_dt
    return d
```
Notes
- Prefer method chaining in real pipelines; expanded form shown for clarity.
- Consider `convert_dtypes()` to adopt nullable dtypes.

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Load CSV with a parsed date column and make it the index. **Hint:** inspect invalid dates before setting the index; `errors="coerce"` turns them into `NaT`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Impute numeric columns with their median and categorical columns with their mode. **Hint:** select columns by dtype and define behavior for an all-missing column whose mode is empty.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Write `clean(df)` returning a fully typed DataFrame. **Hint:** copy first, normalize names/values, convert types, then assert the output contract.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** Predict the results of `pd.to_datetime(..., errors='coerce', utc=True)` for valid text, invalid text, and a timestamp with an offset.

**Reasoning checkpoint:** Invalid text becomes `NaT`; valid values normalize to UTC. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace conversion from object strings to pandas nullable `Int64`, including an empty value.

**Reasoning checkpoint:** Nullable integer dtype can represent `<NA>` without becoming float. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Implement a cleaner that normalizes column names, parses an event time, converts quantity, and returns a copy plus a quality summary.

**Reasoning checkpoint:** Record invalid counts before dropping or imputing anything. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Repair an in-place operation performed on a chained selection.

**Reasoning checkpoint:** Use assignment on the owned copy and avoid `inplace=True` on a temporary object. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Choose behavior for an all-missing numeric column whose median is also missing. Reject, use a domain default, or preserve missing—and justify.

**Reasoning checkpoint:** A statistical fallback cannot be computed from zero observations. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Profile before cleaning, preserve raw input, and make every conversion, imputation, and rejection rule observable and testable.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Explicit conversions

```python
import pandas as pd

timestamps = pd.to_datetime(
    pd.Series(["2025-01-01", "not-a-date", "2025-01-01T02:00:00+02:00"]),
    errors="coerce",
    format="mixed",
    utc=True,
)
assert timestamps.isna().tolist() == [False, True, False]

quantities = pd.to_numeric(pd.Series(["2", "", "7"]), errors="coerce").astype("Int64")
assert quantities.astype("string").tolist() == ["2", pd.NA, "7"]
```

### Practices 3–5 — Cleaner plus evidence

```python
def clean_events(source: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Return a cleaned copy and counts of conversion failures."""

    cleaned = source.copy()
    cleaned.columns = [str(name).strip().casefold().replace(" ", "_")
                       for name in cleaned.columns]
    cleaned["event_time"] = pd.to_datetime(
        cleaned["event_time"], errors="coerce", utc=True
    )
    cleaned["quantity"] = pd.to_numeric(
        cleaned["quantity"], errors="coerce"
    ).astype("Int64")
    quality = {
        "invalid_event_time": int(cleaned["event_time"].isna().sum()),
        "invalid_quantity": int(cleaned["quantity"].isna().sum()),
    }
    return cleaned, quality


raw = pd.DataFrame(
    {" Event Time ": ["2025-01-01", "bad"], "Quantity": ["2", "many"]}
)
cleaned, quality = clean_events(raw)
assert list(raw.columns) == [" Event Time ", "Quantity"]  # Raw input unchanged.
assert quality == {"invalid_event_time": 1, "invalid_quantity": 1}

# All-missing data has no evidence-based median. This contract preserves
# missing values and reports them; a downstream schema may reject the column.
all_missing = pd.Series([pd.NA, pd.NA], dtype="Float64")
assert pd.isna(all_missing.median())
```
