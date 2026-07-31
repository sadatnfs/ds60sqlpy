# Day 18 — Solutions: Pandas I/O and Cleaning

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**pandas input boundaries, explicit cleaning, and reproducible output**.

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

### Vocabulary used in the worked answers

- **missing value:** an absent observation represented by pandas missing markers.
- **dtype:** a column's stored representation and operation rules.
- **coercion:** conversion that may replace unparseable values with missing data.
- **duplicate:** a repeated row or repeated key under a stated definition.
- **idempotent:** producing the same result when applied again to its own output.
- **data lineage:** evidence about where data came from and how it changed.

### Reference pattern 1 — Normalize text and numeric representations

Count conversion failures instead of silently losing them.

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

**Expected observation:** The names are trimmed, numeric text is converted, and one conversion failure is reported as missing.

### Reference pattern 2 — Write a cleaning function that preserves raw input

Copy at the boundary and make repeated application stable.

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

**Expected observation:** `(' Ada ', True)`. The raw frame is unchanged and the demonstrated cleaner is idempotent on this data.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Load a local CSV into pandas, recording path, encoding, row grain, shape, columns, dtypes, missing counts, and duplicate-key counts before changing anything. **Expected behavior:** produce a compact profile, not a full data dump. **Constraint:** use repository-relative `Path` objects and no network source. **Verify:** restart the kernel and reproduce the same profile.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies pandas input boundaries, explicit cleaning, and reproducible output.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Edge case:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.

**Solution evidence to inspect:** restart the kernel and reproduce the same profile.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Implement `clean_frame(raw)` that trims selected text, converts documented numeric/date fields, handles missing values by written policy, resolves duplicates by a stated key, and returns a new DataFrame. **Constraints:** do not mutate `raw` or use broad `dropna`; record conversion failures. **Verify:** assert raw preservation and `clean_frame(clean_frame(raw)).equals(clean_frame(raw))` for this contract.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies pandas input boundaries, explicit cleaning, and reproducible output.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Edge case:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.

**Solution evidence to inspect:** assert raw preservation and `clean_frame(clean_frame(raw)).equals(clean_frame(raw))` for this contract.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Save only the cleaned frame under an ignored learner artifact directory, then read it back. **Expected behavior:** reloaded row count, columns, and key totals match the in-memory clean frame. **Constraints:** create parent folders with `Path.mkdir`, avoid absolute paths, and do not overwrite raw input. **Verify:** Read the saved file back and assert row count, ordered columns, dtypes/normalization policy, and selected key totals match the cleaned in-memory frame.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies pandas input boundaries, explicit cleaning, and reproducible output.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Edge case:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.

**Solution evidence to inspect:** Read the saved file back and assert row count, ordered columns, dtypes/normalization policy, and selected key totals match the cleaned in-memory frame.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the results of `pd.to_datetime(..., errors='coerce', utc=True)` for valid text, invalid text, and a timestamp with an offset. **Progressive hint:** Invalid text becomes `NaT`; valid values normalize to UTC. **Verify:** Create three input rows and assert valid/offset timestamps normalize to the expected UTC instants while invalid text becomes `NaT` and is counted.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying pandas input boundaries, explicit cleaning, and reproducible output.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Edge case:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.

**Solution evidence to inspect:** Create three input rows and assert valid/offset timestamps normalize to the expected UTC instants while invalid text becomes `NaT` and is counted.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace conversion from object strings to pandas nullable `Int64`, including an empty value. **Progressive hint:** Nullable integer dtype can represent `<NA>` without becoming float. **Verify:** Record value and dtype before/after conversion; assert numeric strings become integers, empty input becomes `<NA>`, and dtype is nullable `Int64`.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the pandas input boundaries, explicit cleaning, and reproducible output model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Edge case:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.

**Solution evidence to inspect:** Record value and dtype before/after conversion; assert numeric strings become integers, empty input becomes `<NA>`, and dtype is nullable `Int64`.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement a cleaner that normalizes column names, parses an event time, converts quantity, and returns a copy plus a quality summary. **Progressive hint:** Record invalid counts before dropping or imputing anything. **Verify:** Assert the cleaner leaves raw unchanged, returns expected normalized columns/dtypes, and reports exact invalid timestamp/quantity counts.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies pandas input boundaries, explicit cleaning, and reproducible output.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Edge case:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.

**Solution evidence to inspect:** Assert the cleaner leaves raw unchanged, returns expected normalized columns/dtypes, and reports exact invalid timestamp/quantity counts.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair an in-place operation performed on a chained selection. **Progressive hint:** Use assignment on the owned copy and avoid `inplace=True` on a temporary object. **Verify:** Reproduce the warning/failure, then assert explicit owned-copy assignment changes only the intended frame and uses no `inplace` temporary mutation.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in pandas input boundaries, explicit cleaning, and reproducible output.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Edge case:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.

**Solution evidence to inspect:** Reproduce the warning/failure, then assert explicit owned-copy assignment changes only the intended frame and uses no `inplace` temporary mutation.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Choose behavior for an all-missing numeric column whose median is also missing. Reject, use a domain default, or preserve missing—and justify. **Progressive hint:** A statistical fallback cannot be computed from zero observations. **Verify:** Run an all-missing fixture and assert the exact chosen reject/default/preserve policy; document why no sample median was available.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from pandas input boundaries, explicit cleaning, and reproducible output.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use pandas for tabular batch cleaning, the `csv` module for simple streaming, and a database when constraints/transactions belong at storage.

**Edge case:** Blank strings versus nulls, locale-formatted numbers, duplicate keys with conflicting fields, empty input, and dtype drift need policy.

**Solution evidence to inspect:** Run an all-missing fixture and assert the exact chosen reject/default/preserve policy; document why no sample median was available.
<!-- END BEGINNER SOLUTION REVIEW -->

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
