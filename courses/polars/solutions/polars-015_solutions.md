# polars-015: explained reference

Evaluate a query under an explicit engine and resource contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Scale the fixture cautiously

Record input size, engine and elapsed time. Do not extrapolate a tiny fixture into a production memory claim.

**Why it holds here:** Raising the row count while keeping group % 5 still lets you check against a Python formula, for example sum(i % 7 for i in range(100, n)) for the filtered query.

**Plausible wrong approach:** Running a much larger input and recording only elapsed time drops the correctness check and invites claims far beyond the measured size.

**How to verify:** Record n, engine and seconds, assert the streaming total equals the formula, and keep the in-memory and streaming results equal at that size.

**Expected:** The exact result still matches the independent formula.

## 2. Change grouping cardinality

Explain why group cardinality affects memory. Streaming does not erase the state required to retain a result for each key.

```python
import polars as pl

frame = pl.DataFrame({"id": range(1000), "value": [i % 7 for i in range(1000)]})
few = (
    frame.lazy()
    .group_by((pl.col("id") % 5).alias("group"))
    .agg(pl.col("value").sum())
    .collect(engine="streaming")
)
many = (
    frame.lazy()
    .group_by((pl.col("id") // 2).alias("pair"))
    .agg(pl.col("value").sum())
    .collect(engine="streaming")
)
assert (few.height, many.height) == (5, 500)
```

**Why it holds here:** Grouping 1000 ids by id % 5 yields 5 groups, while id // 2 yields 500. The engine must hold a partial sum for every group until the input ends.

**Plausible wrong approach:** Assuming streaming keeps memory flat regardless of key count ignores that 500 partial aggregates need 100 times the state of 5.

**How to verify:** Run the answer code and assert heights (5, 500); for a real study vary key cardinality and record peak memory with a process tool.

**Expected:** The result has many more groups.

## 3. Compare collect and sink

The sink changes how the caller receives output, not the intended values. Keep artifact paths separate from input globs.

**Why it holds here:** sink_parquet writes the result to a file instead of returning it, but the query and its values are the same, so readback sorted by group equals the collected frame.

**Plausible wrong approach:** Writing the sink into the same folder the scan globs can feed result.parquet back into the next run.

**How to verify:** As in example_one, read the sink file, sort by group and assert equality with query.collect(engine='streaming').

**Expected:** Readback equals the collected result.

## 4. Include a global sort

Measure the query with that requirement included. Removing the sort to obtain a faster number changes the delivered contract.

```python
import polars as pl

frame = pl.DataFrame({"id": range(1000), "value": [i % 7 for i in range(1000)]})
ordered = (
    frame.lazy()
    .group_by((pl.col("id") % 5).alias("group"))
    .agg(pl.col("value").sum())
    .sort("group")
    .collect(engine="streaming")
)
assert ordered["group"].to_list() == [0, 1, 2, 3, 4]
```

**Why it holds here:** The consumer needs groups in order 0 to 4, so sort('group') is part of the query and part of what any timing measures.

**Plausible wrong approach:** Timing the query without sort and adding it later reports a faster number for output that does not meet the contract.

**How to verify:** Run the answer code and assert ordered['group'] is [0, 1, 2, 3, 4]; include the sort inside any timing loop.

**Expected:** The result obeys the declared order.

## 5. Reject a false batch claim

A two-pass or accumulated-statistic algorithm can implement the global operation. Centering each batch separately produces a different result.

**Why it holds here:** Centering by the full mean needs a value that depends on every row. Example_two in polars-016 shows that batches [1, 2] and [3, 10] give [-0.5, 0.5, -3.5, 3.5] instead of [-3, -2, -1, 6].

**Plausible wrong approach:** Calling the batched version streaming compatible because each batch runs independently confuses executing in batches with computing the intended global result.

**How to verify:** Compute the mean over all rows first, then subtract it; check the two pass output equals the single pass global result.

**Expected:** The answer identifies dependence on global state.

## 6. Report limitations

State the observed inputs, resource configuration and outputs. A maximum supported dataset size requires a separate controlled boundary study.

**Why it holds here:** The fixture supports only this claim: on 1000 rows and this machine the in-memory and streaming engines gave identical sums, here 2702 for ids 100 to 999.

**Plausible wrong approach:** Writing that the pipeline scales to production size extrapolates far beyond 1000 rows without a measured boundary.

**How to verify:** Have someone else read the conclusion and check that every number in it appears in the run's recorded inputs or outputs.

**Expected:** The conclusion is bounded to tested sizes and settings.

## Complete reference

```python
"""polars-015: complete bounded Polars investigation."""

import tempfile
from pathlib import Path

import polars as pl


def example_one():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "source.parquet"
        pl.DataFrame(
            {
                "id": range(1000),
                "group": [i % 5 for i in range(1000)],
                "value": [i % 7 for i in range(1000)],
            }
        ).write_parquet(path)
        query = (
            pl.scan_parquet(path)
            .filter(pl.col("id") >= 100)
            .group_by("group")
            .agg(pl.col("value").sum())
            .sort("group")
        )
        memory = query.collect(engine="in-memory")
        streaming = query.collect(engine="streaming")
        assert memory.equals(streaming)
        assert streaming["value"].sum() == sum(i % 7 for i in range(100, 1000))
        query.sink_parquet(Path(d) / "result.parquet", engine="streaming")
        assert pl.read_parquet(Path(d) / "result.parquet").sort("group").equals(streaming)
        return {"same_result": True, "rows": streaming.to_dicts()}


def example_two():
    frame = pl.DataFrame({"x": range(20)})
    per_row = (
        frame.lazy().with_columns((pl.col("x") * 2).alias("twice")).collect(engine="streaming")
    )
    whole = frame.lazy().select(pl.col("x").sum().alias("total")).collect(engine="streaming")
    assert per_row.height == 20 and whole.height == 1
    assert whole.item() == 190 and per_row["twice"].sum() == 380
    return {"row_map_rows": 20, "reduction_rows": 1, "sum": 190}


def main():
    print(example_one())
    print(example_two())
    print("polars-015 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Demonstrate equal logical results, inspect output materialization, and state which scalability questions remain unmeasured. This is the foundation for honest performance engineering.
