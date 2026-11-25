# Day 18 Solutions: Loading and Cleaning Data with pandas

**Offline teaching data:** the `passenger-outcomes` [synthetic fixture](../../../fixtures/README.md) is invented, so its numbers prove methods, not facts.


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

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Load a local CSV into pandas, recording path, encoding, row grain, shape, columns, dtypes, missing counts, and duplicate-key counts before changing anything. **Expected behavior:** produce a compact profile, not a full data dump. **Constraint:** use repository-relative `Path` objects and no network source. **Verify:** save the first profile values, restart the kernel, and assert the second shape, columns, dtypes, missing counts, and duplicate-key counts exactly match.

**Reasoning:** Recording the profile before any change gives later steps a baseline to check against: shape `(3, 3)`, one exact duplicate row, and one duplicate key, because Ada appears twice at the same event time. Writing the fixture with `Path.write_text` and reading it with an explicit `encoding="utf-8"` makes the second run after a kernel restart produce the same profile, which is what the Verify step compares. Storing counts and dtypes instead of printing the rows keeps the profile compact and safe to share, and `path.as_posix()` records the relative path with forward slashes on every operating system.

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

### Exercise 2: worked answer

**Learner contract:** Implement `clean_frame(raw)` that trims selected text, converts documented numeric/date fields, handles missing values by written policy, resolves duplicates by a stated key, and returns a new DataFrame. **Constraints:** do not mutate `raw` or use broad `dropna`; record conversion failures. **Verify:** assert raw preservation and `clean_frame(clean_frame(raw)).equals(clean_frame(raw))` for this contract.

**Reasoning:** Each step handles one documented problem: header whitespace and case, padded names, quantities stored as text, and timestamps stored as text. `errors="coerce"` turns unparseable values into missing values instead of stopping, so the function records `quantity_parse_failed` before that information is lost: a value that was present and became missing is a conversion failure, not an originally missing value. Carrying the earlier flag forward with `|` is what makes the function idempotent; without it, the second pass would see an already numeric `<NA>`, flag nothing, and `once.equals(twice)` would fail. Deduplication uses the business key `name, event_time` and keeps the first record, and the snapshot comparison proves that `raw` was not modified.

```python
import pandas as pd


def clean_frame(raw: pd.DataFrame) -> pd.DataFrame:
    result = raw.copy()
    result.columns = [column.strip().lower() for column in result.columns]
    result["name"] = result["name"].astype("string").str.strip()
    original_quantity = result["quantity"]
    converted_quantity = pd.to_numeric(original_quantity, errors="coerce")
    new_conversion_failure = original_quantity.notna() & converted_quantity.isna()
    prior_conversion_failure = result.get(
        "quantity_parse_failed",
        pd.Series(False, index=result.index),
    ).fillna(False)
    result["quantity_parse_failed"] = prior_conversion_failure | new_conversion_failure
    result["quantity"] = converted_quantity.astype("Int64")
    result["event_time"] = pd.to_datetime(result["event_time"], errors="coerce", utc=True)
    # Policy: preserve missing/conversion-failed values for review; do
    # not use broad dropna. Keep the first exact business-key record.
    return result.drop_duplicates(["name", "event_time"], keep="first").reset_index(drop=True)


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

### Exercise 3: worked answer

**Learner contract:** Save only the cleaned frame under an ignored learner artifact directory, then read it back. **Expected behavior:** reloaded row count, columns, and key totals match the in-memory clean frame. **Constraints:** create parent folders with `Path.mkdir`, avoid absolute paths, and do not overwrite raw input. **Verify:** Read the saved file back and assert row count, ordered columns, dtypes/normalization policy, and selected key totals match the cleaned in-memory frame.

**Reasoning:** Writing to a separate path, asserted to differ from `raw_path`, guarantees that the raw input is never overwritten. CSV stores only text, so the reloaded frame does not keep the pandas extension dtypes: the nullable `Int64` quantity comes back as `float64` because of the missing value, and the UTC timestamps come back as strings. The normalization policy is therefore applied again after reading (`string`, `Int64`, UTC datetime), and `assert_frame_equal` then confirms that values, column order, and dtypes match the in-memory frame. Comparing totals as well catches a lost or duplicated row even before the dtype step.

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
assert reloaded["quantity_parse_failed"].sum() == once["quantity_parse_failed"].sum()

# CSV stores text, so apply the documented dtype policy again after reading.
restored = reloaded.assign(
    name=reloaded["name"].astype("string"),
    quantity=reloaded["quantity"].astype("Int64"),
    event_time=pd.to_datetime(reloaded["event_time"], utc=True),
)
pd.testing.assert_frame_equal(restored, once)
```

CSV does not preserve every pandas extension dtype, so compare the
documented reload representation rather than assuming perfect dtype
round-trip.

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** Predict the results of `pd.to_datetime(..., errors='coerce', utc=True)` for valid text, invalid text, and a timestamp with an offset. **Progressive hint:** Invalid text becomes `NaT`; valid values normalize to UTC. **Verify:** Create three input rows and assert valid/offset timestamps normalize to the expected UTC instants while invalid text becomes `NaT` and is counted.

**Reasoning:** `utc=True` converts every parsed value to a single time zone: the naive `"2025-01-01"` is treated as UTC, and `"2025-01-01T02:00:00+02:00"` is shifted to 00:00 UTC, so both rows represent the same instant, which the shared implementation for Exercises 4-5 asserts. `errors="coerce"` turns `"not-a-date"` into `NaT` instead of raising, so the failure has to be counted afterwards or it disappears silently. `format="mixed"` matters because the inputs use different layouts: without it, pandas 2 infers one format from the first value, and the offset timestamp is also coerced to `NaT`.

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace conversion from object strings to pandas nullable `Int64`, including an empty value. **Progressive hint:** Nullable integer dtype can represent `<NA>` without becoming float. **Verify:** Record value and dtype before/after conversion; assert numeric strings become integers, empty input becomes `<NA>`, and dtype is nullable `Int64`.

**Reasoning:** `pd.to_numeric(..., errors="coerce")` returns `float64` here, because the empty string becomes `NaN` and NumPy integer arrays have no missing-value marker, so 2 and 7 would become 2.0 and 7.0. `.astype("Int64")`, with a capital I, converts to pandas' nullable integer dtype, which holds whole numbers and `<NA>` together. The shared implementation for Exercises 4-5 prints the dtype before (`object`) and after (`Int64`) and checks the values, which is the evidence the Verify step asks for.

### Exercise 6: answer contract

**Learner contract:** **Implementation:** Implement a cleaner that normalizes column names, parses an event time, converts quantity, and returns a copy plus a quality summary. **Progressive hint:** Record invalid counts before dropping or imputing anything. **Verify:** Assert the cleaner leaves raw unchanged, returns expected normalized columns/dtypes, and reports exact invalid timestamp/quantity counts.

**Reasoning:** The cleaner returns a copy together with a quality dictionary, so the caller receives both the data and the evidence of what failed to convert. Counting `isna()` after coercion counts original gaps and conversion failures together; that is exact for this fixture, which has no original gaps, but the separate flag from Exercise 2 is the stricter design when the difference matters. Header normalization with `strip`, `casefold`, and underscores turns `" Event Time "` into `event_time`, and the assertion on `raw.columns` proves that the input kept its original headers.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** Repair an in-place operation performed on a chained selection. **Progressive hint:** Use assignment on the owned copy and avoid `inplace=True` on a temporary object. **Verify:** Reproduce the warning/failure, then assert explicit owned-copy assignment changes only the intended frame and uses no `inplace` temporary mutation.

**Reasoning:** `owned[missing]["quantity"].fillna(0, inplace=True)` fills a temporary object created by the first selection, so the frame you meant to change keeps its missing value; pandas 2 emits a `SettingWithCopyWarning`, and pandas 3 never updates the original through such a chain. The repair is one explicit assignment on a frame you own, `owned.loc[missing, "quantity"] = 0`, which names the frame, rows, and column in one step. The shared implementation for Exercises 6-8 reproduces the unchanged result first, then shows that the explicit assignment changes `owned` and leaves `cleaned` untouched.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Choose behavior for an all-missing numeric column whose median is also missing. Reject, use a domain default, or preserve missing, and justify. **Progressive hint:** A statistical fallback cannot be computed from zero observations. **Verify:** Run an all-missing fixture and assert the exact chosen reject/default/preserve policy; document why no sample median was available.

**Reasoning:** A median needs at least one observation, so for a column with none, `median()` returns a missing value, and `fillna(median)` would fill nothing while appearing to succeed. The reference preserves the missing values and reports them, because inventing a number would hide the fact that the source sent no data; a schema that requires the column could reject the batch instead. The `impute_median` helper in the shared implementation for Exercises 6-8 makes the policy explicit and testable: it returns an all-missing column unchanged and fills normally when observations exist.

## Expanded mastery lab solutions

Profile before cleaning, preserve raw input, and make every conversion, imputation, and rejection rule observable and testable.

### Shared implementation for Exercises 4-5: Explicit conversions

```python
import pandas as pd

timestamps = pd.to_datetime(
    pd.Series(["2025-01-01", "not-a-date", "2025-01-01T02:00:00+02:00"]),
    errors="coerce",
    format="mixed",
    utc=True,
)
assert timestamps.isna().tolist() == [False, True, False]
assert timestamps[0] == timestamps[2] == pd.Timestamp("2025-01-01T00:00:00Z")
assert int(timestamps.isna().sum()) == 1

raw_quantities = pd.Series(["2", "", "7"])
quantities = pd.to_numeric(raw_quantities, errors="coerce").astype("Int64")
print(raw_quantities.dtype, "->", quantities.dtype)  # object -> Int64
assert str(quantities.dtype) == "Int64"
assert quantities.astype("string").tolist() == ["2", pd.NA, "7"]
```

### Shared implementation for Exercises 6-8: Cleaner plus evidence

```python
def clean_events(source: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Return a cleaned copy and counts of conversion failures."""

    cleaned = source.copy()
    cleaned.columns = [str(name).strip().casefold().replace(" ", "_") for name in cleaned.columns]
    cleaned["event_time"] = pd.to_datetime(cleaned["event_time"], errors="coerce", utc=True)
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce").astype("Int64")
    quality = {
        "invalid_event_time": int(cleaned["event_time"].isna().sum()),
        "invalid_quantity": int(cleaned["quantity"].isna().sum()),
    }
    return cleaned, quality


raw = pd.DataFrame({" Event Time ": ["2025-01-01", "bad"], "Quantity": ["2", "many"]})
cleaned, quality = clean_events(raw)
assert list(raw.columns) == [" Event Time ", "Quantity"]  # Raw input unchanged.
assert quality == {"invalid_event_time": 1, "invalid_quantity": 1}
assert cleaned.columns.tolist() == ["event_time", "quantity"]
assert str(cleaned["quantity"].dtype) == "Int64"

# Chained in-place update: the first selection returns a temporary object.
import warnings

owned = cleaned.copy()
missing = owned["quantity"].isna()
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    owned[missing]["quantity"].fillna(0, inplace=True)
print("chained update:", caught[0].category.__name__ if caught else "no warning")
assert owned["quantity"].isna().sum() == 1  # owned is unchanged
owned.loc[missing, "quantity"] = 0  # one explicit assignment on the owned copy
assert owned["quantity"].tolist() == [2, 0]
assert cleaned["quantity"].isna().sum() == 1  # the source copy is untouched


# All-missing data has no evidence-based median. This contract preserves
# missing values and reports them; a downstream schema may reject the column.
def impute_median(values: pd.Series) -> pd.Series:
    """Fill gaps with the median; return an all-missing column unchanged."""
    if values.notna().sum() == 0:
        return values.copy()  # zero observations, so no sample median exists
    return values.fillna(values.median())


all_missing = pd.Series([pd.NA, pd.NA], dtype="Float64")
# NumPy may warn "Mean of empty slice" here: there are zero observations.
assert pd.isna(all_missing.median())
assert impute_median(all_missing).isna().all()
assert impute_median(pd.Series([1.0, None, 3.0], dtype="Float64")).tolist() == [1.0, 2.0, 3.0]
```
