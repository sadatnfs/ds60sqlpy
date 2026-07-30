# Day 21 — Time Series with pandas

**Level:** Intermediate

Time-series correctness depends on timestamp meaning, time zones, ordering, and
window boundaries—not just the numeric calculation.

## Learning objectives

By the end of this lesson, you can:

- parse timestamps and construct a sorted `DatetimeIndex`;
- distinguish timezone-naive from timezone-aware values;
- localize wall-clock time and convert aware timestamps to UTC;
- resample observations into stated calendar intervals;
- compute row-based and time-based rolling windows.

## Prerequisites

Complete Day 20 (`python-20`): indexes, table grain, grouping, and validation.

## Vocabulary and mental model

- **Timestamp:** one point in time or an unzoned wall-clock reading.
- **Timezone-naive:** no zone/offset; **timezone-aware:** carries location or
  offset rules.
- **Localization:** attach a zone to naive local time; **conversion:** express
  an aware instant in another zone.
- **Frequency:** spacing such as calendar day, business day, or month end.
- **Resampling:** group observations into time bins.
- **Rolling window:** calculation over preceding rows or duration.

Store instants in UTC and preserve the source zone when business meaning depends
on local clocks.

## Worked example

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
index = pd.date_range("2024-01-01", periods=14, freq="D", tz="UTC")
values = pd.Series(rng.integers(1, 10, size=len(index)), index=index)

weekly = values.resample("W-SUN", label="right", closed="right").sum()
trailing_7d = values.rolling("7D", min_periods=1).mean()
```

The seeded generator makes results repeatable. The explicit weekly label and
boundary make the bin definition reviewable.

## Exercises and progressive hints

1. Create a business-day series and compute weekly sums. **Hint:** choose and
   document the weekly boundary (`W-FRI` or `W-SUN`), then reconcile the grand
   total before and after resampling.
2. Add a named local timezone to a timestamp column, then convert it to UTC.
   **Hint:** parse first, use localization only on naive values, and include a
   date near a daylight-saving transition in your tests.

### Additional mastery practice

Keep timestamps timezone-aware at system boundaries, declare resampling windows, and reconcile totals whenever frequency changes.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict the difference between `tz_localize` and `tz_convert`, and which one applies to a naive timestamp.
   **Progressive hint:** Localization assigns meaning; conversion changes representation of an instant.
4. **Tracing:** Trace a three-day rolling mean with `min_periods=1` and identify which observations contribute at the beginning.
   **Progressive hint:** Early windows contain fewer rows when the minimum allows it.
5. **Implementation:** Resample deterministic daily sales to `W-FRI`, then assert the grand total is preserved.
   **Progressive hint:** Document the weekly label/boundary and use sums for additive measures.
6. **Debugging:** Repair a comparison between naive and timezone-aware timestamps.
   **Progressive hint:** Normalize both sides to an aware UTC contract.
7. **Edge case and explanation:** Handle an ambiguous or nonexistent daylight-saving local time and explain why silently guessing may corrupt event order.
   **Progressive hint:** Use explicit `ambiguous`/`nonexistent` policy or reject the input.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- Why is `tz_localize` not interchangeable with `tz_convert`?
- How does a seven-row rolling window differ from `rolling("7D")`?
- Which side of a resample bin contains an exact boundary timestamp?
- Why should a time index be sorted before slicing or rolling?

Expected behavior: weekly sums reconcile with source values, aware timestamps
represent the same instants after UTC conversion, and window choices are stated.

## Common pitfalls and diagnosis

- **Localizing an aware timestamp raises:** use `tz_convert` for already-aware
  values.
- **Daylight-saving times are ambiguous/nonexistent:** choose an explicit
  policy and test those dates rather than silently guessing.
- **Monthly aliases change behavior across versions:** use current explicit
  aliases such as month-end `"ME"` and inspect deprecation warnings.
- **Rolling results begin with missing values:** set `min_periods` deliberately.
- **Resampled totals differ:** inspect missing timestamps, aggregation, bin
  closure, and time zone before blaming arithmetic.

## Continue

- [Open the learner notebook](../notebooks/day21_time_series_pandas.ipynb)
- [Check the separate solution](../solutions/day21_time_series_pandas/day21_solutions.md)
- [Next: Day 22 — Advanced pandas](day22_advanced_pandas_apply_query_eval.md)
