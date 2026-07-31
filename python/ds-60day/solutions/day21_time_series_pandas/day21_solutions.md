# Day 21 — Solutions: Time Series with Pandas

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **time-aware indexes, timezone policy, resampling, rolling windows, and lag features**. Predict each named
result before comparing your attempt with its matching assertions.

A timestamp represents a point or label in time; a duration represents
an elapsed amount. Parsing text is only the first step: decide whether
timestamps are timezone-naive or timezone-aware and what business zone
controls calendar boundaries. Localizing assigns a zone to wall-clock
values; converting changes the representation of an already-known
instant.

Resampling groups a time index into calendar bins and aggregates each
bin. Rolling windows calculate over neighboring observations or elapsed
time. `shift` aligns earlier values with later rows and is central to
lag features. Sort the time index, make duplicate timestamps and missing
intervals explicit, and document boundary/label rules.

### Vocabulary used in the worked answers

- **timestamp:** a date-time value, optionally tied to a timezone.
- **timezone-aware:** carrying an offset/zone interpretation for an instant.
- **localize:** assign a timezone interpretation to naive wall-clock values.
- **convert:** represent an aware instant in another timezone.
- **resample:** group observations into regular time bins.
- **rolling window:** a calculation over neighboring rows or an elapsed interval.

### How to compare an answer

For this lesson's **time-aware indexes, timezone policy, resampling, rolling windows, and lag features** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Parse the supplied timestamp strings, reject unparseable values, localize according to a written source-timezone policy, and convert the result to UTC. **Expected behavior:** the final dtype is timezone-aware UTC and invalid text is reported rather than silently dropped. **Verify:** inspect the earliest/latest instant and demonstrate that conversion preserves the instant.

**Reasoning:** Implement this exact contract as written: Parse the supplied timestamp strings, reject unparseable values, localize according to a written source-timezone policy, and convert the result to UTC. Expected behavior: the final dtype is timezone-aware UTC and invalid text is reported rather than silently dropped. Keep the prompt's named data and constraints visible in the code, then establish this specific result: inspect the earliest/latest instant and demonstrate that conversion preserves the instant. That connects the answer to time-aware indexes, timezone policy, resampling, rolling windows, and lag features.

```python
import pandas as pd

def parse_source_times(values: list[str]) -> pd.Series:
    parsed = pd.Series(pd.to_datetime(values, errors="coerce"))
    if parsed.isna().any():
        bad = [value for value, ok in zip(values, parsed.notna()) if not ok]
        raise ValueError(f"unparseable timestamps: {bad}")
    return (
        parsed.dt.tz_localize(
            "America/Los_Angeles",
            ambiguous="raise",
            nonexistent="raise",
        )
        .dt.tz_convert("UTC")
    )


utc_times = parse_source_times(
    ["2025-01-01 09:00", "2025-01-01 10:00"]
)
assert str(utc_times.dt.tz) == "UTC"
assert utc_times.dt.strftime("%Y-%m-%d %H:%M %Z").tolist() == [
    "2025-01-01 17:00 UTC",
    "2025-01-01 18:00 UTC",
]
try:
    parse_source_times(["not-a-time"])
except ValueError as error:
    assert "not-a-time" in str(error)
else:
    raise AssertionError("unparseable input should remain visible")
```

The written source policy treats naive strings as Los Angeles wall
times. Localization assigns that meaning; conversion then represents
the same instants in UTC. Ambiguous/nonexistent daylight-saving times
raise instead of being guessed.

**Verification evidence:** inspect the earliest/latest instant and demonstrate that conversion preserves the instant.

### Exercise 2 — worked answer

**Learner contract:** Using deterministic daily sales, compute a three-observation rolling mean and weekly `W-FRI` sums. **Constraints:** sort the index, choose `min_periods`, and document weekly labels/boundaries. **Verify:** trace the first three rolling windows by hand and assert weekly sums preserve the grand total.

**Reasoning:** Trace the concrete values in this contract one step at a time: Using deterministic daily sales, compute a three-observation rolling mean and weekly `W-FRI` sums. Constraints: sort the index, choose `min_periods`, and document weekly labels/boundaries. Record the named value, shape, label, or iterator position needed to establish: trace the first three rolling windows by hand and assert weekly sums preserve the grand total. The trace exposes time-aware indexes, timezone policy, resampling, rolling windows, and lag features directly.

```python
import pandas as pd

daily = pd.Series(
    [2, 3, 5, 7, 11, 13, 17],
    index=pd.date_range("2025-01-06", periods=7, freq="D"),
    name="sales",
)
daily = daily.sort_index()
rolling = daily.rolling(3, min_periods=1).mean()
weekly = daily.resample("W-FRI").sum()

assert rolling.iloc[:3].tolist() == [2.0, 2.5, 10 / 3]
assert rolling.iloc[-1] == (11 + 13 + 17) / 3
assert weekly.tolist() == [28, 30]
assert weekly.sum() == daily.sum()
```

`min_periods=1` permits partial windows in the first two rows.
`W-FRI` closes each weekly bin on Friday; sum is valid because sales is
additive, and the reconciliation proves no daily value was lost.

**Verification evidence:** trace the first three rolling windows by hand and assert weekly sums preserve the grand total.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict the difference between `tz_localize` and `tz_convert`, and which one applies to a naive timestamp. **Progressive hint:** Localization assigns meaning; conversion changes representation of an instant. **Verify:** Assert localizing a naive timestamp creates an aware value and converting it to UTC preserves the same instant; show the inappropriate operation raises.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the difference between `tz_localize` and `tz_convert`, and which one applies to a naive timestamp. Progressive hint: Localization assigns meaning; conversion changes representation of an instant. Then compare the prediction with this proof target: Assert localizing a naive timestamp creates an aware value and converting it to UTC preserves the same instant; show the inappropriate operation raises. This makes time-aware indexes, timezone policy, resampling, rolling windows, and lag features observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Assert localizing a naive timestamp creates an aware value and converting it to UTC preserves the same instant; show the inappropriate operation raises.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace a three-day rolling mean with `min_periods=1` and identify which observations contribute at the beginning. **Progressive hint:** Early windows contain fewer rows when the minimum allows it. **Verify:** List source dates contributing to the first three outputs and assert their means for `min_periods=1` exactly.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace a three-day rolling mean with `min_periods=1` and identify which observations contribute at the beginning. Progressive hint: Early windows contain fewer rows when the minimum allows it. Record the named value, shape, label, or iterator position needed to establish: List source dates contributing to the first three outputs and assert their means for `min_periods=1` exactly. The trace exposes time-aware indexes, timezone policy, resampling, rolling windows, and lag features directly.

**Evidence to locate in the grouped implementation:** List source dates contributing to the first three outputs and assert their means for `min_periods=1` exactly.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Resample deterministic daily sales to `W-FRI`, then assert the grand total is preserved. **Progressive hint:** Document the weekly label/boundary and use sums for additive measures. **Verify:** Assert weekly bin labels follow `W-FRI`, every source date belongs to one bin, and weekly sums equal the daily grand total.

**Reasoning:** Make this boundary unambiguous in code: Implementation: Resample deterministic daily sales to `W-FRI`, then assert the grand total is preserved. Progressive hint: Document the weekly label/boundary and use sums for additive measures. Values below, at, and above the named boundary must produce the evidence Assert weekly bin labels follow `W-FRI`, every source date belongs to one bin, and weekly sums equal the daily grand total. Those cases show how time-aware indexes, timezone policy, resampling, rolling windows, and lag features behaves at its edge.

**Evidence to locate in the grouped implementation:** Assert weekly bin labels follow `W-FRI`, every source date belongs to one bin, and weekly sums equal the daily grand total.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a comparison between naive and timezone-aware timestamps. **Progressive hint:** Normalize both sides to an aware UTC contract. **Verify:** Show the naive/aware comparison failure, normalize both to aware UTC, and assert chronological comparison now reflects the intended instants.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a comparison between naive and timezone-aware timestamps. Progressive hint: Normalize both sides to an aware UTC contract. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Show the naive/aware comparison failure, normalize both to aware UTC, and assert chronological comparison now reflects the intended instants. The diagnosis depends on time-aware indexes, timezone policy, resampling, rolling windows, and lag features.

**Evidence to locate in the grouped implementation:** Show the naive/aware comparison failure, normalize both to aware UTC, and assert chronological comparison now reflects the intended instants.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Handle an ambiguous or nonexistent daylight-saving local time and explain why silently guessing may corrupt event order. **Progressive hint:** Use explicit `ambiguous`/`nonexistent` policy or reject the input. **Verify:** Use explicit ambiguous/nonexistent policies on documented DST fixtures and assert the chosen raise/resolve outcome without silently reordering events.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Handle an ambiguous or nonexistent daylight-saving local time and explain why silently guessing may corrupt event order. Progressive hint: Use explicit `ambiguous`/`nonexistent` policy or reject the input. Values below, at, and above the named boundary must produce the evidence Use explicit ambiguous/nonexistent policies on documented DST fixtures and assert the chosen raise/resolve outcome without silently reordering events. Those cases show how time-aware indexes, timezone policy, resampling, rolling windows, and lag features behaves at its edge.

**Evidence to locate in the grouped implementation:** Use explicit ambiguous/nonexistent policies on documented DST fixtures and assert the chosen raise/resolve outcome without silently reordering events.

## Expanded mastery lab solutions

Keep timestamps timezone-aware at system boundaries, declare resampling windows, and reconcile totals whenever frequency changes.

### Shared implementation for Exercises 3–4 — Timezone and rolling-window semantics

`tz_localize` assigns a timezone to naive wall-clock values. `tz_convert`
represents already-aware instants in another timezone. With
`min_periods=1`, the first rolling mean uses one row, the second uses two, and
later values use up to three.

### Shared implementation for Exercises 5–7 — Reconciled resampling and explicit DST policy

```python
import pandas as pd

daily = pd.Series(
    range(1, 11),
    index=pd.date_range("2025-01-01", periods=10, freq="D", tz="UTC"),
    name="sales",
)
weekly = daily.resample("W-FRI").sum()
assert weekly.sum() == daily.sum()

naive = pd.Timestamp("2025-01-01 12:00")
aware = naive.tz_localize("America/New_York").tz_convert("UTC")
boundary = pd.Timestamp("2025-01-01 17:00", tz="UTC")
assert aware == boundary

# 2025-03-09 02:30 never occurred in America/New_York.
nonexistent = pd.DatetimeIndex(["2025-03-09 02:30"]).tz_localize(
    "America/New_York", nonexistent="NaT"
)
assert nonexistent.isna().all()

# Rejecting or marking the value missing is safer than silently inventing an
# instant unless the product contract explicitly defines a shift policy.
```
