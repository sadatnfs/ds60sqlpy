# polars-017: Performance measurements with correctness controls

## Level and prerequisites

Advanced. Direct prerequisites: `polars-010`, `polars-015`, `polars-016`

**Outcome:** Produce a reviewable performance comparison with a correctness oracle.

## Question and mechanism

A timing number becomes useful only when the measured work is defined. Query construction, schema discovery, file I/O, computation, conversion to Python objects and serialization can contribute different costs. A benchmark that times only construction of a lazy object has not measured execution. A warm repeated query over an in-memory frame is also different from a cold read of a newly opened dataset.

The first case collects the query on every repetition and checks its answer. It reports a median across a small number of observations rather than declaring the smallest observed value to be a stable property. The fixture is deliberately modest so it can run inside the classroom budget. No assertion says that one engine must beat another, because tiny timings are noisy and hardware dependent.

Performance comparisons must preserve the output contract. An unordered result can be compared as a set or multiset when order is irrelevant; an ordered consumer needs the sorting cost included. The second case distinguishes bag equality from sequence equality. This prevents a supposed optimization from silently removing an ordering requirement.

## Syntax and data contract

perf_counter measures elapsed time around the actual collect call. Record the engine and the number of repetitions. estimated_size describes the frame's buffer estimate, not the whole process peak or every temporary allocation. Sort only when that is part of the intended comparison, and account for its cost explicitly.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Measure completed work with an independent answer

The query filters twenty thousand synthetic values and sums them. A Python expression computes the expected answer independently. Every measured execution must match it, and the report includes row count and an estimate of input buffer size.

**Expected evidence:** All five results match the exact sum; timings are nonnegative and the median is reported without a speed claim.

```python
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
```


## Worked case 2: Separate sequence from content

The second case compares a shuffled frame with a sorted one. Sorting the shuffled result establishes the same identified content, while the unsorted sequence may differ. The original frame also remains unchanged.

**Expected evidence:** The sorted values are [1,2,3]; bag equality holds after sorting.

```python
import polars as pl


def example_two():
    frame = pl.DataFrame({"x": [3, 1, 2]})
    ordered = frame.sort("x")
    arbitrary = frame.sample(fraction=1, shuffle=True, seed=17)
    assert ordered["x"].to_list() == [1, 2, 3]
    assert arbitrary.sort("x").equals(ordered)
    assert frame.equals(pl.DataFrame({"x": [3, 1, 2]}))
    return {"bag_equality": True, "input_not_mutated": True, "sequence": arbitrary["x"].to_list()}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Include file I/O

Move fixture creation outside timing and measure a fresh file scan separately.

**Check:** The report identifies what was included.

**Hint:** Setup and timed work are different phases.


### 2. Vary scale

Repeat at two declared input sizes.

**Check:** Answers remain correct at both sizes.

**Hint:** Keep the data-generation rule stable.


### 3. Report variability

Keep every timing rather than only the fastest.

**Check:** The raw repetitions and a summary are available.

**Hint:** A median does not replace raw observations.


### 4. Avoid a false memory claim

Explain why estimated_size is not process peak memory.

**Check:** The answer names temporary and runtime overhead.

**Hint:** Buffer size is one component.


### 5. Preserve sorting cost

Compare two queries whose consumers require ordered rows.

**Check:** Both timings include the required order.

**Hint:** Equivalent values alone are insufficient.


### 6. Write a bounded conclusion

Summarize what the benchmark demonstrates.

**Check:** It names data size, engine, version and measurement scope.

**Hint:** Do not generalize from one machine.


## Diagnose errors and misleading results

Near-zero timings may indicate that execution was omitted. Very different answers indicate a correctness problem before they indicate a performance win. Avoid benchmark assertions such as always faster, and keep expensive experiments within declared limits. A slow first run may include compilation or initialization that later runs do not repeat.

## Transfer to independent work

Produce a reviewable performance comparison with a correctness oracle. State the measured operation, data size, ordering requirement, cache regime and resource environment, and retain all repetitions. Use the result to choose the next experiment rather than treating a microbenchmark as a production guarantee.

## Primary references

- [Polars documentation: Performance measurements with correctness controls](https://docs.pola.rs/user-guide/lazy/execution/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-017`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
