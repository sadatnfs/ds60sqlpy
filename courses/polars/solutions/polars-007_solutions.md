# polars-007: explained reference

Define time semantics before aggregating a dataset.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Display another zone

Use convert_time_zone with a valid IANA zone. A timezone is not just a fixed UTC offset because historical and seasonal rules can differ.

**Expected:** The instants and elapsed seconds stay unchanged.

## 2. Explain a naive value

The date, region and repeated-time policy can matter. Do not silently assume the learner machine timezone is the data source timezone.

**Expected:** The answer identifies unresolved instant interpretation.

## 3. Test the end boundary

The filter time < end excludes the boundary, which avoids double counting when the next period starts there.

**Expected:** It belongs to the following period.

## 4. Test a zero-length window

No instant is both greater than or equal to start and strictly less than the same endpoint. Treat an accidental zero-duration configuration as a separate validation issue.

**Expected:** The half-open window is empty.

## 5. Compare duration definitions

Use calendar boundaries for local daily reporting and elapsed durations for timeout or physical-rate calculations. State the intended unit.

**Expected:** The answer allows a calendar day with a different elapsed duration.

## 6. Add a late arrival

A historical feature calculation needs both event and availability rules. The later as-of lesson demonstrates how an old event can still leak future knowledge.

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

Define time semantics before aggregating a dataset. Use an explicit zone and interval convention, test the boundary observations and retain separate event and availability timestamps. Apply those rules consistently across training, dashboards and incremental data products.
