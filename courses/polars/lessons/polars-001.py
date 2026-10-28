"""polars-001: worked starting point; complete the guide's six changes."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"order_id": [1, 2, 3], "units": [2, 1, 4], "price": [5, 8, 3]})
    result = frame.with_columns((pl.col("units") * pl.col("price")).alias("revenue"))
    assert frame.shape == (3, 3) and result.shape == (3, 4)
    assert result["revenue"].to_list() == [10, 8, 12]
    assert result.select(pl.col("revenue").sum()).item() == 30
    assert "revenue" not in frame.columns
    return {"rows": result.to_dicts(), "total_revenue": 30}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Append an order with units 3 and price 4, then predict the total before running.
# TODO 2: Return order_id and revenue only.
# TODO 3: Replace the final sum with a mean and describe its denominator.
# TODO 4: Check that calling with_columns did not add revenue to frame.
# TODO 5: Filter to orders above 100 and explain whether a zero-row output is an error.
# TODO 6: Add a duplicate order_id and test the proposed key.
