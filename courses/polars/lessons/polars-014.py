"""polars-014: worked starting point; complete the guide's six changes."""

import polars as pl


def example_one():
    requests = pl.DataFrame({"id": [1, 2, 3], "time": [2, 5, 9]}).sort("time")
    features = pl.DataFrame({"time": [1, 4, 8], "value": [10, 20, 30]}).sort("time")
    past = requests.join_asof(features, on="time", strategy="backward", tolerance=2)
    future = requests.join_asof(features, on="time", strategy="forward")
    assert past["value"].to_list() == [10, 20, 30]
    assert future["value"].to_list() == [20, 30, None]
    return {"past_only": past.to_dicts(), "lookahead_counterexample": future.to_dicts()}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Change tolerance from 2 to 0 in the first case.
# TODO 2: Create two customers with overlapping timestamps.
# TODO 3: Move the late revision known time from 7 to 4.
# TODO 4: Set a feature known time equal to the prediction cutoff.
# TODO 5: Add a request before every available feature.
# TODO 6: State the two temporal questions you would test in a real store.
