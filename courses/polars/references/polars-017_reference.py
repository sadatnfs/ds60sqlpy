"""polars-017: complete bounded Polars investigation."""

from statistics import median
from time import perf_counter

import polars as pl


def example_one():
    frame = pl.DataFrame({"id": range(20000), "x": [i % 101 for i in range(20000)]})
    query = frame.lazy().filter(pl.col("x") > 50).select(pl.col("x").sum().alias("sum"))
    expected = sum(i % 101 for i in range(20000) if i % 101 > 50)
    timings = []
    for _ in range(5):
        start = perf_counter()
        result = query.collect(engine="in-memory")
        timings.append(perf_counter() - start)
        assert result.item() == expected
    assert all(value >= 0 for value in timings)
    return {
        "rows": frame.height,
        "answer": expected,
        "median_seconds": median(timings),
        "fixture_bytes": frame.estimated_size(),
    }


def example_two():
    frame = pl.DataFrame({"x": [3, 1, 2]})
    ordered = frame.sort("x")
    arbitrary = frame.sample(fraction=1, shuffle=True, seed=17)
    assert ordered["x"].to_list() == [1, 2, 3]
    assert arbitrary.sort("x").equals(ordered)
    assert frame.equals(pl.DataFrame({"x": [3, 1, 2]}))
    return {"bag_equality": True, "input_not_mutated": True, "sequence": arbitrary["x"].to_list()}


def main():
    print(example_one())
    print(example_two())
    print("polars-017 reference checks passed")


if __name__ == "__main__":
    main()
