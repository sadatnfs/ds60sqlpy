"""polars-009: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame(
        {
            "id": [3, 1, 2, 4],
            "customer": ["A", "A", "B", "A"],
            "time": [2, 1, 1, 3],
            "value": [5, 2, 7, 4],
        }
    )
    output = frame.sort("customer", "time", "id").with_columns(
        pl.col("value").cum_sum().over("customer").alias("running"),
        pl.col("value").shift(1).over("customer").alias("previous"),
    )
    assert output["running"].to_list() == [2, 7, 11, 7]
    assert output["previous"].to_list() == [None, 2, 5, None]
    assert output.height == frame.height
    return {"ordered_windows": output.to_dicts()}


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [2.0, 6.0, 9.0]})
    centered = frame.with_columns(
        (pl.col("value") - pl.col("value").mean().over("group")).alias("centered")
    )
    assert centered["centered"].to_list() == [-2.0, 2.0, 0.0]
    assert frame.group_by("group").agg(pl.col("value").mean()).height == 2
    assert centered.height == 3
    return {"row_preserving_values": centered["centered"].to_list(), "grouped_rows": 2}


def main():
    print(example_one())
    print(example_two())
    print("polars-009 reference checks passed")


if __name__ == "__main__":
    main()
