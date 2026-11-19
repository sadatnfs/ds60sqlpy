"""mle-003: both worked cases; complete the guide's six changes."""


def example_one():
    import polars as pl

    events = pl.DataFrame(
        {
            "customer": [1, 1, 1, 2],
            "time": [1, 3, 8, 2],
            "known": [1, 5, 8, 2],
            "amount": [2, 4, 9, 3],
        }
    )
    requests = pl.DataFrame({"request": [10, 11, 12], "customer": [1, 1, 2], "cutoff": [4, 9, 4]})
    eligible = requests.join(events, on="customer").filter(
        (pl.col("time") < pl.col("cutoff")) & (pl.col("known") <= pl.col("cutoff"))
    )
    totals = (
        eligible.group_by("request")
        .agg(pl.col("amount").sum().alias("sum"), pl.len().alias("count"))
        .sort("request")
    )
    assert totals.to_dicts() == [
        {"request": 10, "sum": 2, "count": 1},
        {"request": 11, "sum": 15, "count": 3},
        {"request": 12, "sum": 3, "count": 1},
    ]
    return {"features": totals.to_dicts(), "event_end_is_exclusive": True}


def example_two():
    import polars as pl

    requests = pl.DataFrame({"request": [1, 2, 3]})
    selected = pl.DataFrame({"request": [1, 2], "value": [0.0, 4.0]})
    joined = requests.join(selected, on="request", how="left", validate="1:1")
    assert joined["value"].to_list() == [0.0, 4.0, None]
    assert joined.height == 3
    return {"zero_and_missing_are_distinct": True, "coverage": 2 / 3}


if __name__ == "__main__":
    print(example_one())
    print(example_two())

# TODO 1: Change the event boundary deliberately and compare the result.
# TODO 2: Create a request for an entity with no eligible history.
# TODO 3: Provide two selected feature rows for one request.
# TODO 4: Describe the decision for a true zero versus absent history.
# TODO 5: Reconcile the number of requests before and after feature construction.
# TODO 6: Describe how to avoid an unrestricted large candidate join.
