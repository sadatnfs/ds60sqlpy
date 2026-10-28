# polars-010: explained reference

Explain a lazy query in terms of its requested result and observable execution plan.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change a threshold

A result assertion is the first correctness check. The optimizer may choose a different physical strategy without changing this answer.

**Expected:** Only id 3 remains with doubled value 40.

## 2. Add an unused column

A lazy file scan can avoid reading irrelevant columns when supported. That observation does not prove zero I/O for every file format or expression.

**Expected:** The selected result is unchanged.

## 3. Compare eager and lazy results

Use equivalent inputs and operations. Compare timing only after verifying equality and describing whether I/O is inside the measured interval.

**Expected:** The sorted frames are equal.

## 4. Test a group counterexample

The before-filtered pipeline would still keep A because it observes only 11. The boundary case demonstrates why order is semantically important.

**Expected:** Its group mean is 6 and the strict >6 filter still rejects it.

## 5. Locate execution

Schema resolution or metadata access may still read information, but the DataFrame result is produced by collect. Do not claim a pipeline ran because a LazyFrame object printed.

**Expected:** collect performs result execution.

## 6. Review a plan assertion

Test values, schemas and invariants. Review plan features and measured behavior when investigating performance rather than using a textual snapshot as the only correctness oracle.

**Expected:** The answer separates format changes from semantic changes.

## Complete reference

```python
"""polars-010: complete bounded Polars investigation."""

import tempfile
from pathlib import Path

import polars as pl


def example_one():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "events.parquet"
        pl.DataFrame(
            {"id": [1, 2, 3], "amount": [5, 12, 20], "unused": ["x", "y", "z"]}
        ).write_parquet(path)
        query = (
            pl.scan_parquet(path)
            .filter(pl.col("amount") >= 10)
            .select("id", (pl.col("amount") * 2).alias("doubled"))
        )
        schema = query.collect_schema()
        assert schema.names() == ["id", "doubled"]
        result = query.collect(engine="streaming").sort("id")
        assert result.to_dict(as_series=False) == {"id": [2, 3], "doubled": [24, 40]}
        print(query.explain(optimized=True))
        return {"result": result.to_dicts(), "planned_columns": schema.names()}


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [1, 9, 8]})
    after = (
        frame.lazy()
        .group_by("group")
        .agg(pl.col("value").mean().alias("mean"))
        .filter(pl.col("mean") > 6)
        .collect()
    )
    before = (
        frame.lazy()
        .filter(pl.col("value") > 6)
        .group_by("group")
        .agg(pl.col("value").mean().alias("mean"))
        .collect()
        .sort("group")
    )
    assert after["group"].to_list() == ["B"]
    assert before["group"].to_list() == ["A", "B"]
    return {"group_filter": after.to_dicts(), "changed_population": before.to_dicts()}


def main():
    print(example_one())
    print(example_two())
    print("polars-010 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Explain a lazy query in terms of its requested result and observable execution plan. Produce an eager reference, a bounded lazy result and one deliberately non-equivalent rewrite. This prepares you to review performance changes without confusing optimization with a change in the analytical question.
