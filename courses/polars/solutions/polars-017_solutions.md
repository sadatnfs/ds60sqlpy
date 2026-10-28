# polars-017: explained reference

Produce a reviewable performance comparison with a correctness oracle.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Include file I/O

Do not count fixture generation as query execution unless that is the workflow under evaluation. Record the filesystem and cache conditions where relevant.

**Expected:** The report identifies what was included.

## 2. Vary scale

A scaling observation requires comparable work and resource settings. Two points do not establish a universal complexity curve or an operational capacity limit.

**Expected:** Answers remain correct at both sizes.

## 3. Report variability

Report the distribution and context. Large variability may come from scheduling, I/O caches, compilation or background activity.

**Expected:** The raw repetitions and a summary are available.

## 4. Avoid a false memory claim

Use an appropriate process-level measurement for a peak claim, and specify whether shared buffers and child processes are counted.

**Expected:** The answer names temporary and runtime overhead.

## 5. Preserve sorting cost

Removing sort changes the delivered contract. If order is unnecessary, document that decision and compare multiset equality instead.

**Expected:** Both timings include the required order.

## 6. Write a bounded conclusion

State the measured result and uncertainty. A claim about production throughput needs representative data, concurrency, failure behavior and service-level requirements.

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

Produce a reviewable performance comparison with a correctness oracle. State the measured operation, data size, ordering requirement, cache regime and resource environment, and retain all repetitions. Use the result to choose the next experiment rather than treating a microbenchmark as a production guarantee.
