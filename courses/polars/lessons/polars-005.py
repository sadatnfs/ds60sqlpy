"""polars-005: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Pool all three rate rows without grouping.
# TODO 2: Add a group with 0 successes and 0 trials.
# TODO 3: Describe when an equal-group average would be appropriate.
# TODO 4: Compare input row count with the number of group keys.
# TODO 5: Keep success and trial counts beside each estimated rate.
# TODO 6: Decide whether to retain group B in the measurement summary.
