"""polars-004: worked starting point; complete the guide's six changes."""

import math

import polars as pl


def example_one():
    frame = pl.DataFrame({"x": [1.0, None, float("nan"), 4.0]})
    assert frame["x"].null_count() == 1
    assert frame.select(pl.col("x").is_nan().fill_null(False).sum()).item() == 1
    only_nulls = frame.with_columns(pl.col("x").fill_null(0))
    assert math.isnan(only_nulls["x"][2])
    cleaned = frame.with_columns(pl.col("x").fill_nan(None)).with_columns(pl.col("x").fill_null(0))
    assert cleaned["x"].to_list() == [1.0, 0.0, 0.0, 4.0]
    return {"missing_categories": {"null": 1, "nan": 1}, "policy_values": cleaned["x"].to_list()}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Count observations that are neither null nor NaN.
# TODO 2: Add a flag before replacing absent values.
# TODO 3: Compute the mean of the two observed finite values and compare with zero filling.
# TODO 4: Filter a Boolean field under a keep-unknown policy.
# TODO 5: Evaluate false OR unknown and true OR unknown.
# TODO 6: Generate NaN through an invalid floating operation and keep its cause separate from
#    absent measurement.
