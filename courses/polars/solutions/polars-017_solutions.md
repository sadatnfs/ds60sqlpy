# polars-017: explained reference

Produce a reviewable performance comparison with a correctness oracle.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Include file I/O

Do not count fixture generation as query execution unless that is the workflow under evaluation. Record the filesystem and cache conditions where relevant.

**Why it holds here:** Writing the fixture to Parquet is setup; reading it with scan_parquet is part of the query. Timing them separately shows how much of the number is file reading.

**Plausible wrong approach:** Starting the timer before the frame is built adds Python list creation for 20,000 rows to a number reported as query time.

**How to verify:** Report setup seconds, scan plus query seconds and query only seconds as separate lines, each with the file size and whether the file was freshly written.

**Expected:** The report identifies what was included.

## 2. Vary scale

A scaling observation requires comparable work and resource settings. Two points do not establish a universal complexity curve or an operational capacity limit.

```python
import polars as pl

for size in (20_000, 200_000):
    frame = pl.DataFrame({"x": [i % 101 for i in range(size)]})
    answer = frame.lazy().filter(pl.col("x") > 50).select(pl.col("x").sum()).collect().item()
    assert answer == sum(i % 101 for i in range(size) if i % 101 > 50)
```

**Why it holds here:** Both sizes compare against a plain Python sum: 747450 for 20,000 rows and 7474500 for 200,000 rows, because each block of 101 values contributes the same amount.

**Plausible wrong approach:** Reporting only the two timings and calling the ratio linear scaling turns two points without a correctness check into a growth claim.

**How to verify:** Run the answer code so both assertions pass, then record time per row at each size and state that two points do not establish a curve.

**Expected:** Answers remain correct at both sizes.

## 3. Report variability

Report the distribution and context. Large variability may come from scheduling, I/O caches, compilation or background activity.

```python
from statistics import median
from time import perf_counter

import polars as pl

query = (
    pl.LazyFrame({"x": [i % 101 for i in range(20_000)]})
    .filter(pl.col("x") > 50)
    .select(pl.col("x").sum())
)
timings = []
for _ in range(5):
    start = perf_counter()
    query.collect(engine="in-memory")
    timings.append(perf_counter() - start)
report = {"raw_seconds": timings, "median_seconds": median(timings)}
assert len(report["raw_seconds"]) == 5
```

**Why it holds here:** Keeping all five raw timings shows spread; the median summarizes them without hiding a slow first run caused by warmup or caching.

**Plausible wrong approach:** Reporting only the minimum picks the luckiest run and makes the query look faster than a typical execution.

**How to verify:** Run the answer code, then check len(raw_seconds) == 5 and that median_seconds lies between min and max of the raw list.

**Expected:** The raw repetitions and a summary are available.

## 4. Avoid a false memory claim

Use an appropriate process-level measurement for a peak claim, and specify whether shared buffers and child processes are counted.

**Why it holds here:** estimated_size reports the bytes of the frame's buffers, about the fixture data, not the process peak during a query, which includes temporaries, the Python runtime and allocator overhead.

**Plausible wrong approach:** Quoting fixture_bytes from example_one as memory use understates the peak and says nothing about the query's intermediate state.

**How to verify:** Measure process peak with a tool such as resource.getrusage before and after the query, and report it beside estimated_size with their definitions.

**Expected:** The answer names temporary and runtime overhead.

## 5. Preserve sorting cost

Removing sort changes the delivered contract. If order is unnecessary, document that decision and compare multiset equality instead.

**Why it holds here:** If both consumers require rows sorted, the sort belongs in both timed queries. Example_two shows a shuffled frame equals the sorted one only after sorting.

**Plausible wrong approach:** Dropping the sort from one query makes it look faster while it delivers a sequence like the shuffled one, which fails an ordered consumer.

**How to verify:** Include sort in both timings and assert each output equals its sorted version; if order truly is irrelevant, compare with sort applied before equality.

**Expected:** Both timings include the required order.

## 6. Write a bounded conclusion

State the measured result and uncertainty. A claim about production throughput needs representative data, concurrency, failure behavior and service-level requirements.

**Why it holds here:** The benchmark shows the filtered sum 747450 on 20,000 rows with the in-memory engine and a median time on this machine; nothing about other data or concurrency.

**Plausible wrong approach:** Stating rows per second as a production throughput figure ignores the representative data, concurrency and failure handling such a claim needs.

**How to verify:** Check the conclusion names the row count, engine, Polars version and whether I/O was included, and that it claims nothing outside those settings.

**Expected:** It names data size, engine, version and measurement scope.

## Complete reference

```python
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
```

## Interpretation

State the measured operation, data size, ordering requirement, cache regime and resource environment, and retain all repetitions. Use the result to choose the next experiment rather than treating a microbenchmark as a production guarantee.
