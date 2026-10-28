"""polars-002: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"x": [1, 2, 3]})
    output = frame.with_columns(
        (pl.col("x") + 1).alias("x"), (pl.col("x") * 10).alias("old_x_times_ten")
    )
    assert output.to_dict(as_series=False) == {"x": [2, 3, 4], "old_x_times_ten": [10, 20, 30]}
    sequential = frame.with_columns((pl.col("x") + 1).alias("x")).with_columns(
        (pl.col("x") * 10).alias("new_x_times_ten")
    )
    assert sequential["new_x_times_ten"].to_list() == [20, 30, 40]
    return {"parallel_context": output.to_dicts(), "explicit_dependency": sequential.to_dicts()}


def example_two():
    frame = pl.DataFrame({"status": ["paid", "pending", "paid"], "amount": [5, 7, 11]})
    output = frame.select(
        pl.when(pl.col("status") == pl.lit("paid"))
        .then(pl.col("amount"))
        .otherwise(pl.lit(0))
        .alias("recognized")
    )
    assert output["recognized"].to_list() == [5, 0, 11]
    assert frame.select(pl.lit("paid").alias("literal")).item() == "paid"
    try:
        frame.select(pl.col("missing"))
    except pl.exceptions.ColumnNotFoundError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"recognized": output.to_dicts(), "missing_column_rejected": rejected}


def main():
    print(example_one())
    print(example_two())
    print("polars-002 reference checks passed")


if __name__ == "__main__":
    main()
