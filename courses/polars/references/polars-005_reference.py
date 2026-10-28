"""polars-005: complete bounded Polars investigation."""

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


def main():
    print(example_one())
    print(example_two())
    print("polars-005 reference checks passed")


if __name__ == "__main__":
    main()
