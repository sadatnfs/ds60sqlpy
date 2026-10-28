"""polars-002: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Increment x by 2 before the dependent multiplication.
# TODO 2: Keep x unchanged and create incremented_x.
# TODO 3: Produce a column containing the word paid for every row.
# TODO 4: Recognize pending amounts at half value and paid amounts at full value.
# TODO 5: Attempt to use a newly named alias in the same call before a second context exists.
# TODO 6: Write the same recognized amounts with a filter plus an aggregate.
