"""polars-014: complete bounded Polars investigation."""

import polars as pl


def example_one():
    requests = pl.DataFrame({"id": [1, 2, 3], "time": [2, 5, 9]}).sort("time")
    features = pl.DataFrame({"time": [1, 4, 8], "value": [10, 20, 30]}).sort("time")
    past = requests.join_asof(features, on="time", strategy="backward", tolerance=2)
    future = requests.join_asof(features, on="time", strategy="forward")
    assert past["value"].to_list() == [10, 20, 30]
    assert future["value"].to_list() == [20, 30, None]
    return {"past_only": past.to_dicts(), "lookahead_counterexample": future.to_dicts()}


def example_two():
    requests = pl.DataFrame({"request": [1, 2], "customer": [10, 10], "cutoff": [5, 9]})
    features = pl.DataFrame(
        {"customer": [10, 10, 10], "event": [2, 4, 8], "known": [3, 7, 8], "value": [10, 999, 30]}
    )
    candidates = requests.join(features, on="customer").filter(
        (pl.col("event") <= pl.col("cutoff")) & (pl.col("known") <= pl.col("cutoff"))
    )
    correct = (
        candidates.sort("request", "event", "known").group_by("request", maintain_order=True).last()
    )
    assert correct["value"].to_list() == [10, 30]
    leaking = (
        requests.join(features, on="customer")
        .filter(pl.col("event") <= pl.col("cutoff"))
        .sort("request", "event")
        .group_by("request", maintain_order=True)
        .last()
    )
    assert leaking["value"].to_list() == [999, 30]
    return {"available_values": [10, 30], "event_time_only_values": [999, 30]}


def main():
    print(example_one())
    print(example_two())
    print("polars-014 reference checks passed")


if __name__ == "__main__":
    main()
