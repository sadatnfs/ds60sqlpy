"""polars-005: both worked cases; complete the guide's six changes."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "successes": [1, 9, 1], "trials": [1, 99, 2]})
    output = (
        frame.group_by("group")
        .agg(
            pl.col("successes").sum().alias("successes"),
            pl.col("trials").sum().alias("trials"),
            pl.len().alias("rows"),
        )
        .with_columns((pl.col("successes") / pl.col("trials")).alias("rate"))
        .sort("group")
    )
    assert output["rate"].to_list() == [0.1, 0.5]
    naive = (
        frame.filter(pl.col("group") == "A")
        .select((pl.col("successes") / pl.col("trials")).mean())
        .item()
    )
    assert abs(naive - 0.1) > 0.4
    return {"weighted_rates": output.to_dicts(), "wrong_equal_row_mean": naive}


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [2, None, None]})
    result = (
        frame.group_by("group")
        .agg(
            pl.len().alias("rows"),
            pl.col("value").count().alias("observed"),
            pl.col("value").mean().alias("mean"),
        )
        .sort("group")
    )
    assert result["rows"].to_list() == [2, 1]
    assert result["observed"].to_list() == [1, 0]
    assert result["mean"].to_list() == [2.0, None]
    return {"grain": "one row per group", "summary": result.to_dicts()}


if __name__ == "__main__":
    print(example_one())
    print(example_two())

# TODO 1: Pool all three rate rows without grouping.
# TODO 2: Add a group with 0 successes and 0 trials.
# TODO 3: Describe when an equal-group average would be appropriate.
# TODO 4: Compare input row count with the number of group keys.
# TODO 5: Keep success and trial counts beside each estimated rate.
# TODO 6: Decide whether to retain group B in the measurement summary.
