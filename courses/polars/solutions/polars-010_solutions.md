# polars-010: explained reference

Explain a lazy query in terms of its requested result and observable execution plan.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change a threshold

A result assertion is the first correctness check. The optimizer may choose a different physical strategy without changing this answer.

```python
import tempfile
from pathlib import Path

import polars as pl

with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "events.parquet"
    pl.DataFrame({"id": [1, 2, 3], "amount": [5, 12, 20], "unused": ["x", "y", "z"]}).write_parquet(
        path
    )
    query = (
        pl.scan_parquet(path)
        .filter(pl.col("amount") >= 15)
        .select("id", (pl.col("amount") * 2).alias("doubled"))
    )
    assert query.collect().to_dict(as_series=False) == {"id": [3], "doubled": [40]}
```

**Why it holds here:** Amounts 5, 12 and 20 meet the threshold 15 only at id 3, and doubling 20 gives 40, so the collected result is exactly id [3] and doubled [40].

**Plausible wrong approach:** Inspecting the explain output for a pushed down filter shows the optimizer's plan, not the answer; a plan can look right while the threshold has the wrong comparison.

**How to verify:** Run the answer code and assert the collected dict equals {'id': [3], 'doubled': [40]}, then change 15 to 12 and confirm ids [2, 3] return.

**Expected:** Only id 3 remains with doubled value 40.

## 2. Add an unused column

A lazy file scan can avoid reading irrelevant columns when supported. That observation does not prove zero I/O for every file format or expression.

**Why it holds here:** The final select keeps only id and doubled, so a large unused text column can change how much is read but cannot change what is returned.

**Plausible wrong approach:** Claiming that projection pushdown proves the large column was never read goes beyond the test; the result says nothing about bytes touched.

**How to verify:** Add the extra text column to the written file and assert the collected result and collect_schema names are unchanged.

**Expected:** The selected result is unchanged.

## 3. Compare eager and lazy results

Use equivalent inputs and operations. Compare timing only after verifying equality and describing whether I/O is inside the measured interval.

**Why it holds here:** Eager read_parquet followed by the same filter and select applies identical operations, so after sorting by id both frames should hold ids [2, 3] and doubled [24, 40] for the reference threshold.

**Plausible wrong approach:** Comparing wall time first and correctness second can reward a version that reads a different file or skips the filter.

**How to verify:** Sort both results by id and assert eager.equals(lazy_result) before running any timing.

**Expected:** The sorted frames are equal.

## 4. Test a group counterexample

The before-filtered pipeline would still keep A because it observes only 11. The boundary case demonstrates why order is semantically important.

```python
import polars as pl

frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [1, 11, 8]})
means = frame.group_by("group").agg(pl.col("value").mean().alias("mean")).sort("group")
assert means["mean"].to_list() == [6.0, 8.0]
assert means.filter(pl.col("mean") > 6)["group"].to_list() == ["B"]
```

**Why it holds here:** Group A with values 1 and 11 has mean 6.0, and 6 is not greater than 6, so the group level filter keeps only B with mean 8.0.

**Plausible wrong approach:** Filtering rows above 6 before grouping keeps A's 11 alone, giving mean 11 and a different population, as example_two shows with A's 9.

**How to verify:** Run the answer code: means is [6.0, 8.0] and the filtered group list is ['B'].

**Expected:** Its group mean is 6 and the strict >6 filter still rejects it.

## 5. Locate execution

Schema resolution or metadata access may still read information, but the DataFrame result is produced by collect. Do not claim a pipeline ran because a LazyFrame object printed.

**Why it holds here:** Building scan_parquet, filter and select only records a plan; the DataFrame result exists after query.collect(), which is where the work runs.

**Plausible wrong approach:** Printing the LazyFrame and seeing its plan text as proof that data was processed confuses a plan description with an executed result.

**How to verify:** Check that the built query is a pl.LazyFrame and that only query.collect() returns a pl.DataFrame, here with ids [2, 3] for the reference threshold.

**Expected:** collect performs result execution.

## 6. Review a plan assertion

Test values, schemas and invariants. Review plan features and measured behavior when investigating performance rather than using a textual snapshot as the only correctness oracle.

**Why it holds here:** The explain text depends on the Polars version and optimizer details, so a snapshot of it fails when formatting changes even though results are the same.

**Plausible wrong approach:** A full string equality test forces updates on every upgrade and teaches reviewers to rubber stamp them, which lets a real semantic change slip through.

**How to verify:** Assert the result values and collect_schema names instead, and if a plan property matters, check only that a filter node appears.

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

Produce an eager reference, a bounded lazy result and one deliberately non-equivalent rewrite. This prepares you to review performance changes without confusing optimization with a change in the analytical question.
