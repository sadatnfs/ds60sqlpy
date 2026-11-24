# polars-007: explained reference

Define time semantics before aggregating a dataset.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Display another zone

Use convert_time_zone with a valid IANA zone. A timezone is not just a fixed UTC offset because historical and seasonal rules can differ.

```python
import polars as pl

frame = pl.DataFrame({"stamp": ["2024-03-10T06:30:00+00:00", "2024-03-10T07:30:00+00:00"]})
utc = frame.select(pl.col("stamp").str.to_datetime(time_zone="UTC").alias("utc"))
tokyo = utc.with_columns(pl.col("utc").dt.convert_time_zone("Asia/Tokyo").alias("tokyo"))
assert tokyo["tokyo"].dt.hour().to_list() == [15, 16]
assert tokyo["tokyo"].dt.epoch("s").to_list() == tokyo["utc"].dt.epoch("s").to_list()
assert (tokyo["tokyo"][1] - tokyo["tokyo"][0]).total_seconds() == 3600
```

**Why it holds here:** convert_time_zone changes only the wall clock label attached to each instant. In Asia/Tokyo the two observations read 15:30 and 16:30, yet the epoch seconds equal the UTC epoch seconds and the gap is still 3600.

**Plausible wrong approach:** Using replace_time_zone keeps the 06:30 and 07:30 wall clock digits and declares them Tokyo time, which moves both instants by nine hours and silently corrupts any later join on time.

**How to verify:** Run the answer code: the hours assert gives [15, 16], the epoch lists match, and the difference between the two Tokyo values is 3600 seconds.

**Expected:** The instants and elapsed seconds stay unchanged.

## 2. Explain a naive value

The date, region and repeated-time policy can matter. Do not silently assume the learner machine timezone is the data source timezone.

**Why it holds here:** A bare 01:30 has no date and no zone, so it cannot be placed on the timeline. On 2024-03-10 in America/New_York, 01:30 exists once, while 02:30 never exists and on the November change 01:30 occurs twice.

**Plausible wrong approach:** Parsing it with the laptop's local zone produces a definite looking instant whose meaning depends on where the notebook ran, not on where the data came from.

**How to verify:** Write down the source zone and date from the data contract, then confirm that the same text parsed under two different zones yields two different epoch values.

**Expected:** The answer identifies unresolved instant interpretation.

## 3. Test the end boundary

The filter time < end excludes the boundary, which avoids double counting when the next period starts there.

```python
from datetime import UTC, datetime

import polars as pl

times = [datetime(2024, 1, day, tzinfo=UTC) for day in (1, 2, 3, 3)]
frame = pl.DataFrame({"time": times, "amount": [2, 3, 5, 7]})
start, end = times[0], times[2]
period = frame.filter((pl.col("time") >= start) & (pl.col("time") < end))
following = frame.filter(pl.col("time") >= end)
assert period["amount"].sum() == 5
assert following["amount"].to_list() == [5, 7]
```

**Why it holds here:** The predicate time >= start and time < end includes January 1 and 2 and excludes January 3, so the two January 3 rows with amounts 5 and 7 land in the following window only.

**Plausible wrong approach:** Using time <= end puts amount 5 into both the current and the next period, so summing adjacent periods would count it twice.

**How to verify:** Run the answer code: the period sums to 5 (2 plus 3) and the following filter returns [5, 7], so the two windows together cover all four rows exactly once.

**Expected:** It belongs to the following period.

## 4. Test a zero-length window

No instant is both greater than or equal to start and strictly less than the same endpoint. Treat an accidental zero-duration configuration as a separate validation issue.

**Why it holds here:** With start equal to end, no timestamp can satisfy time >= start and time < start at once, so the filter returns zero rows for any input.

**Plausible wrong approach:** Treating the empty output as a real quiet period hides a configuration mistake; a window of zero length should be caught when the bounds are validated, before any data is read.

**How to verify:** Set end = start in the boundary fixture and assert the filtered height is 0, then add an explicit check that end > start and confirm it fires.

**Expected:** The half-open window is empty.

## 5. Compare duration definitions

Use calendar boundaries for local daily reporting and elapsed durations for timeout or physical-rate calculations. State the intended unit.

**Why it holds here:** In America/New_York the local calendar day 2024-03-10 lasts 23 elapsed hours because the clock jumps from 02:00 to 03:00; the reference shows 01:30 to 03:30 local as only 3600 seconds apart.

**Plausible wrong approach:** Adding a fixed 24 hour duration to local midnight on that date lands at 01:00 on March 11 rather than at the next midnight, so a daily bucket built that way drifts.

**How to verify:** Compute next local midnight minus local midnight for 2024-03-10 in New York and expect 23 hours, while a UTC day remains 24 hours.

**Expected:** The answer allows a calendar day with a different elapsed duration.

## 6. Add a late arrival

A historical feature calculation needs both event and availability rules. The later as-of lesson demonstrates how an old event can still leak future knowledge.

**Why it holds here:** An event dated January 1 that only arrived on January 5 was not knowable on January 2. Keeping event_time and ingested_at as separate columns lets a feature use the arrival rule.

**Plausible wrong approach:** Overwriting event_time with the arrival time loses when it happened, and keeping only event_time makes a backfill include data that a live system could not have seen.

**How to verify:** Filter for features as of January 2 using ingested_at <= cutoff and confirm the late event is excluded, while an event_time filter alone would include it.

**Expected:** The two timestamps remain separate.

## Complete reference

```python
"""polars-007: complete bounded Polars investigation."""

from datetime import UTC, datetime

import polars as pl


def example_one():
    frame = pl.DataFrame({"stamp": ["2024-03-10T06:30:00+00:00", "2024-03-10T07:30:00+00:00"]})
    parsed = frame.with_columns(pl.col("stamp").str.to_datetime(time_zone="UTC").alias("utc"))
    local = parsed.with_columns(
        pl.col("utc").dt.convert_time_zone("America/New_York").alias("local")
    )
    assert local["local"].dt.hour().to_list() == [1, 3]
    assert (local["utc"][1] - local["utc"][0]).total_seconds() == 3600
    return {"display_hours": [1, 3], "elapsed_seconds": 3600}


def example_two():
    timestamps = [
        datetime(2024, 1, 1, tzinfo=UTC),
        datetime(2024, 1, 2, tzinfo=UTC),
        datetime(2024, 1, 3, tzinfo=UTC),
    ]
    frame = pl.DataFrame({"time": timestamps, "amount": [2, 3, 5]})
    start, end = timestamps[0], timestamps[2]
    period = frame.filter((pl.col("time") >= start) & (pl.col("time") < end))
    assert period["amount"].sum() == 5
    assert frame.filter(pl.col("time") >= end)["amount"].sum() == 5
    assert period.height + frame.filter(pl.col("time") >= end).height == frame.height
    return {"half_open_total": 5, "next_period_total": 5}


def main():
    print(example_one())
    print(example_two())
    print("polars-007 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Use an explicit zone and interval convention, test the boundary observations and retain separate event and availability timestamps. Apply those rules consistently across training, dashboards and incremental data products.
