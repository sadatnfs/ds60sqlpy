"""polars-004: both worked cases; complete the guide's six changes."""

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


def example_two():
    frame = pl.DataFrame({"id": [1, 2, 3], "flag": [True, False, None]})
    assert frame.filter(pl.col("flag"))["id"].to_list() == [1]
    assert frame.filter(pl.col("flag").fill_null(True))["id"].to_list() == [1, 3]
    truth = pl.DataFrame({"a": [True, False, None], "b": [None, None, False]}).select(
        (pl.col("a") & pl.col("b")).alias("and"), (pl.col("a") | pl.col("b")).alias("or")
    )
    assert truth["and"].to_list() == [None, False, False]
    assert truth["or"].to_list() == [True, None, None]
    return {"filter_true": [1], "three_valued_logic": truth.to_dicts()}


if __name__ == "__main__":
    print(example_one())
    print(example_two())

# TODO 1: Count observations that are neither null nor NaN.
# TODO 2: Add a flag before replacing absent values.
# TODO 3: Compute the mean of the two observed finite values and compare with zero filling.
# TODO 4: Filter a Boolean field under a keep-unknown policy.
# TODO 5: Evaluate false OR unknown and true OR unknown.
# TODO 6: Generate NaN through an invalid floating operation and keep its cause separate from
#    absent measurement.
