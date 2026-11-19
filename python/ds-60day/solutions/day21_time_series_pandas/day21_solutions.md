# Day 21 Solutions: Time Series with pandas

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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Parse the supplied timestamp strings, reject unparseable values, localize according to a written source-timezone policy, and convert the result to UTC. **Expected behavior:** the final dtype is timezone-aware UTC and invalid text is reported rather than silently dropped. **Verify:** inspect the earliest/latest instant and demonstrate that conversion preserves the instant.

**Reasoning:** A naive string such as `"2025-01-01 09:00"` carries no time zone, so the code must state where it came from: `tz_localize("America/Los_Angeles")` attaches that meaning, and `tz_convert("UTC")` then expresses the same instants in UTC, 17:00 and 18:00, because Los Angeles is eight hours behind UTC in January. `errors="coerce"` followed by an explicit check turns unparseable text into a `ValueError` that names the bad values, instead of `NaT` rows that vanish in later steps. `ambiguous="raise"` and `nonexistent="raise"` refuse to guess daylight-saving edge cases, so a bad record stops the load instead of shifting an event by an hour.

```python
import pandas as pd


def parse_source_times(values: list[str]) -> pd.Series:
    parsed = pd.Series(pd.to_datetime(values, errors="coerce"))
    if parsed.isna().any():
        bad = [value for value, ok in zip(values, parsed.notna()) if not ok]
        raise ValueError(f"unparseable timestamps: {bad}")
    return parsed.dt.tz_localize(
        "America/Los_Angeles",
        ambiguous="raise",
        nonexistent="raise",
    ).dt.tz_convert("UTC")


utc_times = parse_source_times(["2025-01-01 09:00", "2025-01-01 10:00"])
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

### Exercise 2: worked answer

**Learner contract:** Using deterministic daily sales, compute a three-observation rolling mean and weekly `W-FRI` sums. **Constraints:** sort the index, choose `min_periods`, and document weekly labels/boundaries. **Verify:** trace the first three rolling windows by hand and assert weekly sums preserve the grand total.

**Reasoning:** Trace the windows by hand: with `min_periods=1`, the first window holds only 2, the second holds 2 and 3, and the third holds 2, 3, and 5, so the means are 2.0, 2.5, and 10/3. `W-FRI` closes each weekly bin on a Friday and labels it with that Friday: Monday 6 January to Friday 10 January sum to 28, and the weekend values for 11 and 12 January fall in the bin labelled Friday 17 January, giving 30. Summing is valid because sales are additive, and `weekly.sum() == daily.sum()` proves that no day was lost or counted twice.

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

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict the difference between `tz_localize` and `tz_convert`, and which one applies to a naive timestamp. **Progressive hint:** Localization assigns meaning; conversion changes representation of an instant. **Verify:** Assert localizing a naive timestamp creates an aware value and converting it to UTC preserves the same instant; show the inappropriate operation raises.

**Reasoning:** `tz_localize` is for naive values: it states which wall clock the value was read from and creates an aware timestamp. `tz_convert` is for aware values: it keeps the instant and changes only how it is displayed, so `in_utc == localized` is `True` even though the printed hours differ. Each method rejects the other kind of input with a `TypeError` that names the correct method, which the shared implementation for Exercises 3-4 demonstrates.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace a three-day rolling mean with `min_periods=1` and identify which observations contribute at the beginning. **Progressive hint:** Early windows contain fewer rows when the minimum allows it. **Verify:** List source dates contributing to the first three outputs and assert their means for `min_periods=1` exactly.

**Reasoning:** `rolling(3, min_periods=1)` looks at the current row and up to two earlier rows; at the start fewer rows exist, and `min_periods=1` produces a result as soon as one value is available. Iterating over the rolling object in the shared implementation for Exercises 3-4 lists the contributing dates for the first three outputs: 6 January alone, then 6-7 January, then 6-8 January. With the default, `min_periods` equal to the window size, the first two outputs would be `NaN` instead.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Resample deterministic daily sales to `W-FRI`, then assert the grand total is preserved. **Progressive hint:** Document the weekly label/boundary and use sums for additive measures. **Verify:** Assert weekly bin labels follow `W-FRI`, every source date belongs to one bin, and weekly sums equal the daily grand total.

**Reasoning:** Each weekly bin ends on a Friday and carries that Friday as its label, so 1-3 January (Wednesday to Friday) form a short first bin labelled 3 January, and 4-10 January form the second bin, labelled 10 January. The shared implementation for Exercises 5-7 checks that every label is a Friday, that the bin counts add up to the 10 source days, and that the weekly sum equals the daily total, which together prove that each day landed in exactly one bin. A sum is right for an additive measure such as sales; averaging daily means across bins of different sizes would need weights.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair a comparison between naive and timezone-aware timestamps. **Progressive hint:** Normalize both sides to an aware UTC contract. **Verify:** Show the naive/aware comparison failure, normalize both to aware UTC, and assert chronological comparison now reflects the intended instants.

**Reasoning:** Python cannot order a naive timestamp against an aware one, because the naive value does not say which instant it means, so the comparison raises `TypeError` instead of guessing. The repair localizes the naive value according to the written policy, here New York wall time, and converts it to UTC; both sides are then aware, and comparisons reflect real instants. Normalizing once, where data enters the program, keeps the rest of the code free of mixed comparisons.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Handle an ambiguous or nonexistent daylight-saving local time and explain why silently guessing may corrupt event order. **Progressive hint:** Use explicit `ambiguous`/`nonexistent` policy or reject the input. **Verify:** Use explicit ambiguous/nonexistent policies on documented DST fixtures and assert the chosen raise/resolve outcome without silently reordering events.

**Reasoning:** On 9 March 2025, New York clocks jumped from 02:00 to 03:00, so 02:30 never happened; on 2 November 2025, 01:30 happened twice, first in EDT and then in EST. Guessing either case silently can move an event by an hour and place it before something that happened earlier. The shared implementation for Exercises 5-7 marks the nonexistent time as `NaT` so it can be counted, and resolves the repeated time only with an explicit per-row flag, which places the two events at 05:30 and 06:30 UTC; with the default `ambiguous="raise"`, pandas refuses the input instead.

## Expanded mastery lab solutions

Keep timestamps timezone-aware at system boundaries, declare resampling windows, and reconcile totals whenever frequency changes.

### Shared implementation for Exercises 3-4: Timezone and rolling-window semantics

`tz_localize` assigns a timezone to naive wall-clock values. `tz_convert`
represents already-aware instants in another timezone. With
`min_periods=1`, the first rolling mean uses one row, the second uses two, and
later values use up to three.

```python
import pandas as pd

naive = pd.Timestamp("2025-01-01 09:00")
localized = naive.tz_localize("America/Los_Angeles")  # assigns meaning
in_utc = localized.tz_convert("UTC")  # same instant, new representation
assert localized.tzinfo is not None and in_utc == localized
assert str(in_utc) == "2025-01-01 17:00:00+00:00"
for wrong_call in (lambda: naive.tz_convert("UTC"), lambda: localized.tz_localize("UTC")):
    try:
        wrong_call()
    except TypeError as error:
        print(error)
    else:
        raise AssertionError("each method should reject the other kind of timestamp")

sales = pd.Series([2, 3, 5, 7], index=pd.date_range("2025-01-06", periods=4, freq="D"))
contributors = [list(window.index.strftime("%m-%d")) for window in sales.rolling(3, min_periods=1)]
assert contributors[:3] == [["01-06"], ["01-06", "01-07"], ["01-06", "01-07", "01-08"]]
assert sales.rolling(3, min_periods=1).mean().iloc[:3].tolist() == [2.0, 2.5, 10 / 3]
assert sales.rolling(3).mean().iloc[:2].isna().all()  # default min_periods is 3
```

### Shared implementation for Exercises 5-7: Reconciled resampling and explicit DST policy

```python
import pandas as pd

daily = pd.Series(
    range(1, 11),
    index=pd.date_range("2025-01-01", periods=10, freq="D", tz="UTC"),
    name="sales",
)
weekly = daily.resample("W-FRI").sum()
assert weekly.sum() == daily.sum()
assert (weekly.index.dayofweek == 4).all()  # every label is a Friday
assert weekly.index.strftime("%Y-%m-%d").tolist() == ["2025-01-03", "2025-01-10"]
assert daily.resample("W-FRI").count().tolist() == [3, 7]  # 10 days, each in one bin
assert weekly.tolist() == [6, 49]

naive = pd.Timestamp("2025-01-01 12:00")
boundary = pd.Timestamp("2025-01-01 17:00", tz="UTC")
try:
    print(naive < boundary)
except TypeError as error:
    print("naive vs aware:", error)
else:
    raise AssertionError("a naive/aware comparison should fail")
aware = naive.tz_localize("America/New_York").tz_convert("UTC")
assert aware == boundary
assert pd.Timestamp("2025-01-01 16:59", tz="UTC") < aware

# 2025-03-09 02:30 never occurred in America/New_York.
nonexistent = pd.DatetimeIndex(["2025-03-09 02:30"]).tz_localize(
    "America/New_York", nonexistent="NaT"
)
assert nonexistent.isna().all()
assert int(nonexistent.isna().sum()) == 1  # counted, not silently shifted

# 2025-11-02 01:30 happened twice in America/New_York: first EDT, then EST.
repeated = pd.DatetimeIndex(["2025-11-02 01:30", "2025-11-02 01:30"])
resolved = repeated.tz_localize("America/New_York", ambiguous=[True, False])
assert resolved.tz_convert("UTC").strftime("%H:%M").tolist() == ["05:30", "06:30"]

# Rejecting or marking the value missing is safer than silently inventing an
# instant unless the product contract explicitly defines a shift policy.
```
