"""polars-007: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Convert the same UTC observations to a second named timezone.
# TODO 2: Describe what information is missing from 01:30 without a zone or date.
# TODO 3: Add an observation exactly equal to end.
# TODO 4: Set start equal to end.
# TODO 5: Explain the difference between one calendar day and 24 elapsed hours around a clock
#    change.
# TODO 6: Give an event an old event time but a later ingestion time.
