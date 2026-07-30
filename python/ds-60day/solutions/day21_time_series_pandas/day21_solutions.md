# Day 21 — Solutions: Time Series with Pandas

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Create a business-day series and compute weekly sums. **Hint:** choose and document the weekly boundary (`W-FRI` or `W-SUN`), then reconcile the grand total before and after resampling.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Add a named local timezone to a timestamp column, then convert it to UTC. **Hint:** parse first, use localization only on naive values, and include a date near a daylight-saving transition in your tests.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict the difference between `tz_localize` and `tz_convert`, and which one applies to a naive timestamp.

**Reasoning checkpoint:** Localization assigns meaning; conversion changes representation of an instant. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace a three-day rolling mean with `min_periods=1` and identify which observations contribute at the beginning.

**Reasoning checkpoint:** Early windows contain fewer rows when the minimum allows it. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Resample deterministic daily sales to `W-FRI`, then assert the grand total is preserved.

**Reasoning checkpoint:** Document the weekly label/boundary and use sums for additive measures. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a comparison between naive and timezone-aware timestamps.

**Reasoning checkpoint:** Normalize both sides to an aware UTC contract. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Handle an ambiguous or nonexistent daylight-saving local time and explain why silently guessing may corrupt event order.

**Reasoning checkpoint:** Use explicit `ambiguous`/`nonexistent` policy or reject the input. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
