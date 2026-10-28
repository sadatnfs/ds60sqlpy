"""polars-017: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Move fixture creation outside timing and measure a fresh file scan separately.
# TODO 2: Repeat at two declared input sizes.
# TODO 3: Keep every timing rather than only the fastest.
# TODO 4: Explain why estimated_size is not process peak memory.
# TODO 5: Compare two queries whose consumers require ordered rows.
# TODO 6: Summarize what the benchmark demonstrates.
