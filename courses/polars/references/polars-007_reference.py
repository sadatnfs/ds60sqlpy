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
