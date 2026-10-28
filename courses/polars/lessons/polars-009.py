"""polars-009: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Change the input ordering and retain the explicit sort.
# TODO 2: Add a same-customer event sharing a timestamp and define its order.
# TODO 3: Compute the running value available before each event.
# TODO 4: Verify that B does not inherit A history.
# TODO 5: Explain why full-dataset group centering can leak validation information.
# TODO 6: Replace the mean window with group_by and inspect row counts.
