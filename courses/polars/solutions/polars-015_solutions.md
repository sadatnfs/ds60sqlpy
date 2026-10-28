# polars-015: explained reference

Evaluate a query under an explicit engine and resource contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Scale the fixture cautiously

Record input size, engine and elapsed time. Do not extrapolate a tiny fixture into a production memory claim.

**Expected:** The exact result still matches the independent formula.

## 2. Change grouping cardinality

Explain why group cardinality affects memory. Streaming does not erase the state required to retain a result for each key.

**Expected:** The result has many more groups.

## 3. Compare collect and sink

The sink changes how the caller receives output, not the intended values. Keep artifact paths separate from input globs.

**Expected:** Readback equals the collected result.

## 4. Include a global sort

Measure the query with that requirement included. Removing the sort to obtain a faster number changes the delivered contract.

**Expected:** The result obeys the declared order.

## 5. Reject a false batch claim

A two-pass or accumulated-statistic algorithm can implement the global operation. Centering each batch separately produces a different result.

**Expected:** The answer identifies dependence on global state.

## 6. Report limitations

State the observed inputs, resource configuration and outputs. A maximum supported dataset size requires a separate controlled boundary study.

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

Evaluate a query under an explicit engine and resource contract. Demonstrate equal logical results, inspect output materialization, and state which scalability questions remain unmeasured. This is the foundation for honest performance engineering.
