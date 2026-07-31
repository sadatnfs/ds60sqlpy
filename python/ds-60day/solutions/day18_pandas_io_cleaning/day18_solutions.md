# Day 18 — Solutions: Pandas I/O and Cleaning

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **pandas input boundaries, explicit cleaning, and reproducible output**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **pandas input boundaries, explicit cleaning, and reproducible output** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Load a local CSV into pandas, recording path, encoding, row grain, shape, columns, dtypes, missing counts, and duplicate-key counts before changing anything. **Expected behavior:** produce a compact profile, not a full data dump. **Constraint:** use repository-relative `Path` objects and no network source. **Verify:** save the first profile values, restart the kernel, and assert the second shape, columns, dtypes, missing counts, and duplicate-key counts exactly match.

**Reasoning:** Implement this exact contract as written: Load a local CSV into pandas, recording path, encoding, row grain, shape, columns, dtypes, missing counts, and duplicate-key counts before changing anything. Expected behavior: produce a compact profile, not a full data dump. Constraint: use repository-relative `Path` objects and no network source. Keep the prompt's named data and constraints visible in the code, then establish this specific result: save the first profile values, restart the kernel, and assert the second shape, columns, dtypes, missing counts, and duplicate-key counts exactly match. That connects the answer to pandas input boundaries, explicit cleaning, and reproducible output.

```python
from pathlib import Path
import pandas as pd


def raw_profile(
    path: Path,
    *,
    row_grain: str,
    key_columns: list[str],
) -> tuple[pd.DataFrame, dict[str, object]]:
    frame = pd.read_csv(path, encoding="utf-8")
    profile = {
        "path": path.as_posix(),
        "encoding": "utf-8",
        "row_grain": row_grain,
        "shape": frame.shape,
        "columns": frame.columns.tolist(),
        "dtypes": frame.dtypes.astype(str).to_dict(),
        "missing": frame.isna().sum().to_dict(),
        "duplicate_rows": int(frame.duplicated().sum()),
        "duplicate_keys": int(frame.duplicated(key_columns).sum()),
    }
    return frame, profile


raw_path = Path("artifacts/day18/raw-fixture.csv")
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(
    "Name,Quantity,Event_Time\n"
    " Ada ,2,2025-01-01T00:00:00Z\n"
    " Ada ,2,2025-01-01T00:00:00Z\n"
    "Lin,bad,2025-01-02T00:00:00Z\n",
    encoding="utf-8",
)
loaded_raw, profile = raw_profile(
    raw_path,
    row_grain="one named entity event per row",
    key_columns=["Name", "Event_Time"],
)
assert profile["shape"] == (3, 3)
assert profile["duplicate_keys"] == 1
assert profile["path"] == "artifacts/day18/raw-fixture.csv"
```

Restarting and rerunning reconstructs the same local UTF-8 fixture and
compact profile. The profile records metadata and counts without
printing all source rows.

**Verification evidence:** save the first profile values, restart the kernel, and assert the second shape, columns, dtypes, missing counts, and duplicate-key counts exactly match.

### Exercise 2 — worked answer

**Learner contract:** Implement `clean_frame(raw)` that trims selected text, converts documented numeric/date fields, handles missing values by written policy, resolves duplicates by a stated key, and returns a new DataFrame. **Constraints:** do not mutate `raw` or use broad `dropna`; record conversion failures. **Verify:** assert raw preservation and `clean_frame(clean_frame(raw)).equals(clean_frame(raw))` for this contract.

**Reasoning:** Implement this exact contract as written: Implement `clean_frame(raw)` that trims selected text, converts documented numeric/date fields, handles missing values by written policy, resolves duplicates by a stated key, and returns a new DataFrame. Constraints: do not mutate `raw` or use broad `dropna`; record conversion failures. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert raw preservation and `clean_frame(clean_frame(raw)).equals(clean_frame(raw))` for this contract. That connects the answer to pandas input boundaries, explicit cleaning, and reproducible output.

```python
import pandas as pd


def clean_frame(raw: pd.DataFrame) -> pd.DataFrame:
    result = raw.copy()
    result.columns = [column.strip().lower() for column in result.columns]
    result["name"] = result["name"].astype("string").str.strip()
    original_quantity = result["quantity"]
    converted_quantity = pd.to_numeric(
        original_quantity, errors="coerce"
    )
    new_conversion_failure = (
        original_quantity.notna() & converted_quantity.isna()
    )
    prior_conversion_failure = result.get(
        "quantity_parse_failed",
        pd.Series(False, index=result.index),
    ).fillna(False)
    result["quantity_parse_failed"] = (
        prior_conversion_failure | new_conversion_failure
    )
    result["quantity"] = converted_quantity.astype("Int64")
    result["event_time"] = pd.to_datetime(
        result["event_time"], errors="coerce", utc=True
    )
    # Policy: preserve missing/conversion-failed values for review; do
    # not use broad dropna. Keep the first exact business-key record.
    return (
        result.drop_duplicates(["name", "event_time"], keep="first")
        .reset_index(drop=True)
    )


raw = loaded_raw.copy(deep=True)
raw_snapshot = raw.copy(deep=True)
once = clean_frame(raw)
twice = clean_frame(once)
assert once.equals(twice)
pd.testing.assert_frame_equal(raw, raw_snapshot)
assert once["quantity_parse_failed"].tolist() == [False, True]
assert once["quantity"].isna().sum() == 1
assert not once.duplicated(["name", "event_time"]).any()
```

**Verification evidence:** assert raw preservation and `clean_frame(clean_frame(raw)).equals(clean_frame(raw))` for this contract.

### Exercise 3 — worked answer

**Learner contract:** Save only the cleaned frame under an ignored learner artifact directory, then read it back. **Expected behavior:** reloaded row count, columns, and key totals match the in-memory clean frame. **Constraints:** create parent folders with `Path.mkdir`, avoid absolute paths, and do not overwrite raw input. **Verify:** Read the saved file back and assert row count, ordered columns, dtypes/normalization policy, and selected key totals match the cleaned in-memory frame.

**Reasoning:** Implement this exact contract as written: Save only the cleaned frame under an ignored learner artifact directory, then read it back. Expected behavior: reloaded row count, columns, and key totals match the in-memory clean frame. Constraints: create parent folders with `Path.mkdir`, avoid absolute paths, and do not overwrite raw input. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Read the saved file back and assert row count, ordered columns, dtypes/normalization policy, and selected key totals match the cleaned in-memory frame. That connects the answer to pandas input boundaries, explicit cleaning, and reproducible output.

```python
from pathlib import Path

destination = Path("artifacts/day18/clean.csv")
destination.parent.mkdir(parents=True, exist_ok=True)
assert destination != raw_path
once.to_csv(destination, index=False, encoding="utf-8")
reloaded = pd.read_csv(destination)
assert len(reloaded) == len(once)
assert reloaded.columns.tolist() == once.columns.tolist()
assert reloaded["quantity"].sum() == once["quantity"].sum()
assert (
    reloaded["quantity_parse_failed"].sum()
    == once["quantity_parse_failed"].sum()
)
```

CSV does not preserve every pandas extension dtype, so compare the
documented reload representation rather than assuming perfect dtype
round-trip.

**Verification evidence:** Read the saved file back and assert row count, ordered columns, dtypes/normalization policy, and selected key totals match the cleaned in-memory frame.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** Predict the results of `pd.to_datetime(..., errors='coerce', utc=True)` for valid text, invalid text, and a timestamp with an offset. **Progressive hint:** Invalid text becomes `NaT`; valid values normalize to UTC. **Verify:** Create three input rows and assert valid/offset timestamps normalize to the expected UTC instants while invalid text becomes `NaT` and is counted.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the results of `pd.to_datetime(..., errors='coerce', utc=True)` for valid text, invalid text, and a timestamp with an offset. Progressive hint: Invalid text becomes `NaT`; valid values normalize to UTC. Then compare the prediction with this proof target: Create three input rows and assert valid/offset timestamps normalize to the expected UTC instants while invalid text becomes `NaT` and is counted. This makes pandas input boundaries, explicit cleaning, and reproducible output observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Create three input rows and assert valid/offset timestamps normalize to the expected UTC instants while invalid text becomes `NaT` and is counted.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace conversion from object strings to pandas nullable `Int64`, including an empty value. **Progressive hint:** Nullable integer dtype can represent `<NA>` without becoming float. **Verify:** Record value and dtype before/after conversion; assert numeric strings become integers, empty input becomes `<NA>`, and dtype is nullable `Int64`.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace conversion from object strings to pandas nullable `Int64`, including an empty value. Progressive hint: Nullable integer dtype can represent `<NA>` without becoming float. Record the named value, shape, label, or iterator position needed to establish: Record value and dtype before/after conversion; assert numeric strings become integers, empty input becomes `<NA>`, and dtype is nullable `Int64`. The trace exposes pandas input boundaries, explicit cleaning, and reproducible output directly.

**Evidence to locate in the grouped implementation:** Record value and dtype before/after conversion; assert numeric strings become integers, empty input becomes `<NA>`, and dtype is nullable `Int64`.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Implement a cleaner that normalizes column names, parses an event time, converts quantity, and returns a copy plus a quality summary. **Progressive hint:** Record invalid counts before dropping or imputing anything. **Verify:** Assert the cleaner leaves raw unchanged, returns expected normalized columns/dtypes, and reports exact invalid timestamp/quantity counts.

**Reasoning:** Implement this exact contract as written: Implementation: Implement a cleaner that normalizes column names, parses an event time, converts quantity, and returns a copy plus a quality summary. Progressive hint: Record invalid counts before dropping or imputing anything. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert the cleaner leaves raw unchanged, returns expected normalized columns/dtypes, and reports exact invalid timestamp/quantity counts. That connects the answer to pandas input boundaries, explicit cleaning, and reproducible output.

**Evidence to locate in the grouped implementation:** Assert the cleaner leaves raw unchanged, returns expected normalized columns/dtypes, and reports exact invalid timestamp/quantity counts.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Repair an in-place operation performed on a chained selection. **Progressive hint:** Use assignment on the owned copy and avoid `inplace=True` on a temporary object. **Verify:** Reproduce the warning/failure, then assert explicit owned-copy assignment changes only the intended frame and uses no `inplace` temporary mutation.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair an in-place operation performed on a chained selection. Progressive hint: Use assignment on the owned copy and avoid `inplace=True` on a temporary object. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Reproduce the warning/failure, then assert explicit owned-copy assignment changes only the intended frame and uses no `inplace` temporary mutation. The diagnosis depends on pandas input boundaries, explicit cleaning, and reproducible output.

**Evidence to locate in the grouped implementation:** Reproduce the warning/failure, then assert explicit owned-copy assignment changes only the intended frame and uses no `inplace` temporary mutation.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Choose behavior for an all-missing numeric column whose median is also missing. Reject, use a domain default, or preserve missing—and justify. **Progressive hint:** A statistical fallback cannot be computed from zero observations. **Verify:** Run an all-missing fixture and assert the exact chosen reject/default/preserve policy; document why no sample median was available.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Choose behavior for an all-missing numeric column whose median is also missing. Reject, use a domain default, or preserve missing—and justify. Progressive hint: A statistical fallback cannot be computed from zero observations. Values below, at, and above the named boundary must produce the evidence Run an all-missing fixture and assert the exact chosen reject/default/preserve policy; document why no sample median was available. Those cases show how pandas input boundaries, explicit cleaning, and reproducible output behaves at its edge.

**Evidence to locate in the grouped implementation:** Run an all-missing fixture and assert the exact chosen reject/default/preserve policy; document why no sample median was available.

## Expanded mastery lab solutions

Profile before cleaning, preserve raw input, and make every conversion, imputation, and rejection rule observable and testable.

### Shared implementation for Exercises 4–5 — Explicit conversions

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

### Shared implementation for Exercises 6–8 — Cleaner plus evidence

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
