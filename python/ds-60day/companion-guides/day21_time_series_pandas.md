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

2. Read `python/ds-60day/companion-guides/day21_time_series_pandas.md`, then open `python/ds-60day/notebooks/day21_time_series_pandas.ipynb` from the repository
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

**Lesson outcome:** use day 21 — time series with pandas to practice time-aware indexes, timezone policy, resampling, rolling windows, and lag features
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **timestamp:** a date-time value, optionally tied to a timezone.
- **timezone-aware:** carrying an offset/zone interpretation for an instant.
- **localize:** assign a timezone interpretation to naive wall-clock values.
- **convert:** represent an aware instant in another timezone.
- **resample:** group observations into regular time bins.
- **rolling window:** a calculation over neighboring rows or an elapsed interval.

### Syntax anatomy

`series.resample("W-FRI").sum()` requires a datetime-like index, groups
into weeks labeled/ending Friday, and sums each bin. `rolling(3,
min_periods=1).mean()` uses up to three consecutive rows and permits a
result at the beginning. `shift(1)` moves values one row later without
changing the index.

### Worked example 1 — Parse, index, and resample deterministic daily values

Choose and name the calendar boundary. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

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

**Expected observation**

```text
Both weekly bins together sum to `28`, preserving the additive total. The keys are Sunday-labeled timestamps.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Compare rolling and lagged values

A rolling statistic includes nearby history; a lag exposes a prior observation. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
time_features = pd.DataFrame({
    "sales": daily,
    "rolling_3": daily.rolling(3, min_periods=1).mean(),
    "previous_day": daily.shift(1),
})
time_features.round(2)
```

**Expected observation**

```text
The first rolling mean is `2.0`; the first previous-day value is missing because no earlier row exists.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Inspect dtype, timezone, sort order, duplicates, minimum/maximum, and inferred frequency.
2. Never compare or combine naive and aware timestamps without an explicit policy.
3. For rolling results, list the exact source rows contributing at boundaries.
4. For resampling, document frequency alias, closed side, label, and aggregation semantics.

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

**Useful alternative:** Use row-count windows for evenly sampled observations and time-offset windows when elapsed time—not row count—defines the question.

**Boundary to remember:** Daylight-saving ambiguity/nonexistence, duplicate times, irregular gaps, empty bins, and partial boundary windows need policy.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Parse the supplied timestamp strings, reject unparseable values, localize according to a written source-timezone policy, and convert the result to UTC.
   **Expected behavior:** the final dtype is timezone-aware UTC and invalid text is reported rather than silently dropped.
   **Verify:** inspect the earliest/latest instant and demonstrate that conversion preserves the instant.

2. Using deterministic daily sales, compute a three-observation rolling mean and weekly `W-FRI` sums. **Constraints:** sort the index, choose `min_periods`, and document weekly labels/boundaries.
   **Verify:** trace the first three rolling windows by hand and assert weekly sums preserve the grand total.

### Additional mastery practice

Keep timestamps timezone-aware at system boundaries, declare resampling windows, and reconcile totals whenever frequency changes.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict the difference between `tz_localize` and `tz_convert`, and which one applies to a naive timestamp.
   **Progressive hint:** Localization assigns meaning; conversion changes representation of an instant.
   **Verify:** Assert localizing a naive timestamp creates an aware value and converting it to UTC preserves the same instant; show the inappropriate operation raises.
4. **Tracing:** Trace a three-day rolling mean with `min_periods=1` and identify which observations contribute at the beginning.
   **Progressive hint:** Early windows contain fewer rows when the minimum allows it.
   **Verify:** List source dates contributing to the first three outputs and assert their means for `min_periods=1` exactly.
5. **Implementation:** Resample deterministic daily sales to `W-FRI`, then assert the grand total is preserved.
   **Progressive hint:** Document the weekly label/boundary and use sums for additive measures.
   **Verify:** Assert weekly bin labels follow `W-FRI`, every source date belongs to one bin, and weekly sums equal the daily grand total.
6. **Debugging:** Repair a comparison between naive and timezone-aware timestamps.
   **Progressive hint:** Normalize both sides to an aware UTC contract.
   **Verify:** Show the naive/aware comparison failure, normalize both to aware UTC, and assert chronological comparison now reflects the intended instants.
7. **Edge case and explanation:** Handle an ambiguous or nonexistent daylight-saving local time and explain why silently guessing may corrupt event order.
   **Progressive hint:** Use explicit `ambiguous`/`nonexistent` policy or reject the input.
   **Verify:** Use explicit ambiguous/nonexistent policies on documented DST fixtures and assert the chosen raise/resolve outcome without silently reordering events.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-21`
(Day 21 — Time Series with pandas). Direct catalog prerequisites: `python-20`.
I have completed the direct prerequisites: `python-20`. Emphasize time-aware indexes, timezone policy, resampling, rolling windows, and lag features.
Read `python/ds-60day/companion-guides/day21_time_series_pandas.md` and use the learner notebook
`python/ds-60day/notebooks/day21_time_series_pandas.ipynb`. Do not open or quote anything under `solutions/` unless
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
