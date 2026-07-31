# Day 21 — Solutions: Time Series with Pandas

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**time-aware indexes, timezone policy, resampling, rolling windows, and lag features**.

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

### Reference pattern 1 — Parse, index, and resample deterministic daily values

Choose and name the calendar boundary.

```python
import pandas as pd

daily = pd.Series(
    [2, 3, 5, 7, 11],
    index=pd.date_range("2025-01-01", periods=5, freq="D"),
    name="sales",
)
weekly = daily.resample("W-SUN").sum()
(daily.sum(), weekly.to_dict())
```

**Expected observation:** Both weekly bins together sum to `28`, preserving the additive total. The keys are Sunday-labeled timestamps.

### Reference pattern 2 — Compare rolling and lagged values

A rolling statistic includes nearby history; a lag exposes a prior observation.

```python
time_features = pd.DataFrame({
    "sales": daily,
    "rolling_3": daily.rolling(3, min_periods=1).mean(),
    "previous_day": daily.shift(1),
})
time_features.round(2)
```

**Expected observation:** The first rolling mean is `2.0`; the first previous-day value is missing because no earlier row exists.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Parse the supplied timestamp strings, reject unparseable values, localize according to a written source-timezone policy, and convert the result to UTC. **Expected behavior:** the final dtype is timezone-aware UTC and invalid text is reported rather than silently dropped. **Verify:** inspect the earliest/latest instant and demonstrate that conversion preserves the instant.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies time-aware indexes, timezone policy, resampling, rolling windows, and lag features.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use row-count windows for evenly sampled observations and time-offset windows when elapsed time—not row count—defines the question.

**Edge case:** Daylight-saving ambiguity/nonexistence, duplicate times, irregular gaps, empty bins, and partial boundary windows need policy.

**Solution evidence to inspect:** inspect the earliest/latest instant and demonstrate that conversion preserves the instant.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Using deterministic daily sales, compute a three-observation rolling mean and weekly `W-FRI` sums. **Constraints:** sort the index, choose `min_periods`, and document weekly labels/boundaries. **Verify:** trace the first three rolling windows by hand and assert weekly sums preserve the grand total.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the time-aware indexes, timezone policy, resampling, rolling windows, and lag features model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use row-count windows for evenly sampled observations and time-offset windows when elapsed time—not row count—defines the question.

**Edge case:** Daylight-saving ambiguity/nonexistence, duplicate times, irregular gaps, empty bins, and partial boundary windows need policy.

**Solution evidence to inspect:** trace the first three rolling windows by hand and assert weekly sums preserve the grand total.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the difference between `tz_localize` and `tz_convert`, and which one applies to a naive timestamp. **Progressive hint:** Localization assigns meaning; conversion changes representation of an instant. **Verify:** Assert localizing a naive timestamp creates an aware value and converting it to UTC preserves the same instant; show the inappropriate operation raises.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying time-aware indexes, timezone policy, resampling, rolling windows, and lag features.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use row-count windows for evenly sampled observations and time-offset windows when elapsed time—not row count—defines the question.

**Edge case:** Daylight-saving ambiguity/nonexistence, duplicate times, irregular gaps, empty bins, and partial boundary windows need policy.

**Solution evidence to inspect:** Assert localizing a naive timestamp creates an aware value and converting it to UTC preserves the same instant; show the inappropriate operation raises.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace a three-day rolling mean with `min_periods=1` and identify which observations contribute at the beginning. **Progressive hint:** Early windows contain fewer rows when the minimum allows it. **Verify:** List source dates contributing to the first three outputs and assert their means for `min_periods=1` exactly.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the time-aware indexes, timezone policy, resampling, rolling windows, and lag features model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use row-count windows for evenly sampled observations and time-offset windows when elapsed time—not row count—defines the question.

**Edge case:** Daylight-saving ambiguity/nonexistence, duplicate times, irregular gaps, empty bins, and partial boundary windows need policy.

**Solution evidence to inspect:** List source dates contributing to the first three outputs and assert their means for `min_periods=1` exactly.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Resample deterministic daily sales to `W-FRI`, then assert the grand total is preserved. **Progressive hint:** Document the weekly label/boundary and use sums for additive measures. **Verify:** Assert weekly bin labels follow `W-FRI`, every source date belongs to one bin, and weekly sums equal the daily grand total.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from time-aware indexes, timezone policy, resampling, rolling windows, and lag features.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use row-count windows for evenly sampled observations and time-offset windows when elapsed time—not row count—defines the question.

**Edge case:** Daylight-saving ambiguity/nonexistence, duplicate times, irregular gaps, empty bins, and partial boundary windows need policy.

**Solution evidence to inspect:** Assert weekly bin labels follow `W-FRI`, every source date belongs to one bin, and weekly sums equal the daily grand total.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a comparison between naive and timezone-aware timestamps. **Progressive hint:** Normalize both sides to an aware UTC contract. **Verify:** Show the naive/aware comparison failure, normalize both to aware UTC, and assert chronological comparison now reflects the intended instants.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in time-aware indexes, timezone policy, resampling, rolling windows, and lag features.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use row-count windows for evenly sampled observations and time-offset windows when elapsed time—not row count—defines the question.

**Edge case:** Daylight-saving ambiguity/nonexistence, duplicate times, irregular gaps, empty bins, and partial boundary windows need policy.

**Solution evidence to inspect:** Show the naive/aware comparison failure, normalize both to aware UTC, and assert chronological comparison now reflects the intended instants.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Handle an ambiguous or nonexistent daylight-saving local time and explain why silently guessing may corrupt event order. **Progressive hint:** Use explicit `ambiguous`/`nonexistent` policy or reject the input. **Verify:** Use explicit ambiguous/nonexistent policies on documented DST fixtures and assert the chosen raise/resolve outcome without silently reordering events.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from time-aware indexes, timezone policy, resampling, rolling windows, and lag features.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use row-count windows for evenly sampled observations and time-offset windows when elapsed time—not row count—defines the question.

**Edge case:** Daylight-saving ambiguity/nonexistence, duplicate times, irregular gaps, empty bins, and partial boundary windows need policy.

**Solution evidence to inspect:** Use explicit ambiguous/nonexistent policies on documented DST fixtures and assert the chosen raise/resolve outcome without silently reordering events.
<!-- END BEGINNER SOLUTION REVIEW -->

We work through business-day series with weekly sums, and time zone handling with conversion to UTC.

Contents
- Exercise 1: Business-day time series and weekly sums
- Exercise 2: Add a time zone to a timestamp column and convert to UTC

---

Exercise 1 — Business-day series and weekly sums
```python
import pandas as pd
import numpy as np

# 1) Business-day DatetimeIndex (BDay frequency)
rng = pd.bdate_range('2024-01-01', periods=20)   # business days only

# 2) Create a Series indexed by business days
s = pd.Series(np.arange(len(rng)), index=rng, name='value')

# 3) Resample to weekly sums (W-FRI or W-SUN; pick one and be consistent)
weekly_sum = s.resample('W-FRI').sum()  # week ending Friday

print(s.head())
print(weekly_sum)
```
Line-by-line
- pd.bdate_range gives business days; weekends omitted
- resample requires a DatetimeIndex; choose an anchor (e.g., week ending Friday)

Notes
- If you want calendar weeks regardless of business days, resample still works; missing weekend days are simply absent
- For different anchors: 'W-MON', 'W-SUN', 'W-FRI', etc.

---

Exercise 2 — Time zones and UTC conversion
```python
import pandas as pd

# Example DataFrame with naive timestamps (no tz info)
df = pd.DataFrame({'ts': ['2024-02-01 08:30:00', '2024-02-01 15:45:00'],
                   'value': [10, 20]})

# 1) Parse to timezone-aware timestamps in a local zone (e.g., America/Los_Angeles)
df['ts'] = pd.to_datetime(df['ts']).dt.tz_localize('America/Los_Angeles')

# 2) Convert to UTC for storage/processing
df_utc = df.assign(ts=df['ts'].dt.tz_convert('UTC'))

# 3) Set as index and resample hourly (example)
by_hour = df_utc.set_index('ts').sort_index().resample('h').sum()

print(df)
print(df_utc)
print(by_hour.head())
```
Why this pattern
- Localize first when timestamps are local but naive
- Convert to UTC internally to avoid ambiguity (DST issues); convert back on display

Pitfalls
- Don’t .tz_localize when timestamps already have tz; use .tz_convert instead
- Always sort by time before resample/rolling

---

## Expanded mastery lab solutions

Keep timestamps timezone-aware at system boundaries, declare resampling windows, and reconcile totals whenever frequency changes.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Timezone and rolling-window semantics

`tz_localize` assigns a timezone to naive wall-clock values. `tz_convert`
represents already-aware instants in another timezone. With
`min_periods=1`, the first rolling mean uses one row, the second uses two, and
later values use up to three.

### Practices 3–5 — Reconciled resampling and explicit DST policy

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
