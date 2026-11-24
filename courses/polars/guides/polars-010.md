# polars-010: Lazy plans and optimizer reasoning

## Level and prerequisites

Intermediate. Direct prerequisites: `polars-002`, `polars-005`, `polars-006`

**Outcome:** Explain a lazy query in terms of its requested result and observable execution plan.

## Question and mechanism

A lazy query describes a computation before materializing its result. This gives the query engine an opportunity to combine operations, read only needed columns and move eligible filters toward the data source. The plan is an intermediate representation of the requested computation. It is not a record that a particular amount of work has already happened.

Optimization must preserve semantics. Filtering individual measurements before taking a group mean is different from filtering groups after their mean is calculated. The second worked case deliberately changes that ordering and produces a different population. An optimizer may move operations only when its transformation preserves the requested result. The fact that two pipelines look similar is not evidence that they are interchangeable.

Read explain output as diagnostic evidence about this version and query. Avoid tests that require every line of a printed optimizer plan to remain identical across library releases. Instead test the intended result and inspect meaningful properties such as the selected columns, scan source and filter placement. Performance still needs measurement under a stated data and cache regime.

## Key terms

- **LazyFrame:** A frame that records operations as a query plan and computes nothing until `collect` runs.
- **Logical plan:** The tree of operations a LazyFrame describes, which the optimizer may rewrite and `explain()` displays.
- **Predicate pushdown:** An optimization that moves a filter closer to the data source so fewer rows are read and processed.
- **Projection pushdown:** An optimization that reads only the columns the query actually uses.
- **Semantic equivalence:** Two plans return the same result; filtering measurements before a group mean is not equivalent to filtering groups after it.

## Syntax and data contract

scan_parquet creates a lazy source. filter and select append operations to its plan. collect_schema inspects the planned schema, while collect executes the query using the specified engine. explain(optimized=True) exposes a printable plan. Calling lazy() after eagerly reading the entire file cannot undo the original eager read.

## Run the lesson

Open `polars-010` in `/classroom`. Its starter `main.py` contains both worked cases, "Inspect a pushed-down scan" and "Identify a non-equivalent rewrite", and prints the dictionary each case returns. The prepared `data-engineering` worker runs it in a fresh temporary directory. An `AssertionError` means that an observation differs from the case's stated contract. The inputs are small literal tables. Cases that demonstrate Parquet scans write their files into a temporary directory that is removed when the case returns. No account, network request or package download is involved. Save source and notes before switching lessons.

## Worked case 1: Inspect a pushed-down scan

The first case writes a small Parquet fixture, creates a lazy scan, filters amounts and selects only two outputs. It asserts the schema and result before printing a plan for inspection. The unused input column illustrates why projection can matter.

**Expected evidence:** Ids [2, 3] have doubled values [24, 40], and the result schema contains exactly two fields.

```python
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


if __name__ == "__main__":
    print(example_one())
```

## Worked case 2: Identify a non-equivalent rewrite

The second case contrasts filtering group means with filtering individual values before averaging. Group A has values 1 and 9, so its mean is 5; dropping the low observation changes that mean and the selection decision.

**Expected evidence:** Filtering group means retains only B; filtering values first retains A and B.

```python
import polars as pl


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


if __name__ == "__main__":
    print(example_two())
```

## Practice

The starter contains both worked cases, so a task can change either one. Make each change in a saved copy, run it, and compare the printed result with the task's check before opening the separate explained answers.

### 1. Change a threshold

Raise the amount threshold to 15.

**Check:** Only id 3 remains with doubled value 40.

**Hint:** State the expected rows before inspecting a plan.

### 2. Add an unused column

Add a large text field that the result does not need.

**Check:** The selected result is unchanged.

**Hint:** Inspect projection in the plan.

### 3. Compare eager and lazy results

Compute the same filter and projection eagerly.

**Check:** The sorted frames are equal.

**Hint:** Separate correctness from speed.

### 4. Test a group counterexample

Change group A to values 1 and 11.

**Check:** Its group mean is 6 and the strict >6 filter still rejects it.

**Hint:** The comparison is strict.

### 5. Locate execution

Identify which statement actually materializes the query.

**Check:** collect performs result execution.

**Hint:** Planning is not result evidence.

### 6. Review a plan assertion

Explain why asserting the entire explain string is brittle.

**Check:** The answer separates format changes from semantic changes.

**Hint:** Plans can evolve across versions.

## Diagnose errors and misleading results

If a lazy pipeline appears fast, confirm that it was actually collected. If it reads more than expected, inspect where the file scan becomes an eager object and which expressions require extra columns. If an optimization attempt changes results, return to the row and group semantics before tuning execution settings.

## Transfer to independent work

Produce an eager reference, a bounded lazy result and one deliberately non-equivalent rewrite. This prepares you to review performance changes without confusing optimization with a change in the analytical question.

## Primary references

- [Polars user guide: Optimizations](https://docs.pola.rs/user-guide/lazy/optimizations/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository's `$guide-ds60sqlpy-learning` skill (`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`) for `polars-010`. Inspect the learner's own source and printed output first. Ask for an explanation of LazyFrame, logical plan, predicate pushdown, projection and equivalence in their own words, then give one focused hint at a time. Keep an assertion on this synthetic fixture separate from a claim about an external dataset or deployed service.
