# polars-015: Streaming execution and bounded output

## Level and prerequisites

Advanced. Direct prerequisites: `polars-010`, `polars-011`

**Outcome:** Evaluate a query under an explicit engine and resource contract.

## Question and mechanism

Streaming execution processes suitable parts of a query in batches. This can reduce memory pressure and support writing results without materializing every output row as a Python object. It does not mean that every operator uses constant memory or that any dataset will fit any machine. Joins, sorting, distinct operations and high-cardinality group state still require resources determined by the query and data.

The first case compares two engines on the same lazy query and independently checks its numeric total. Engine selection is separated from correctness. The example is intentionally small, so its successful streaming execution is not a claim about an out-of-memory boundary or a production throughput rate. A meaningful capacity study needs controlled dataset size, measured peak memory and a defined machine budget.

A sink can write a result directly to a file, while collect returns a DataFrame to the caller. The second case contrasts a row-preserving transformation with a global reduction. Both can be evaluated through a streaming path, but they produce different shapes and require different state. Output shape and operator semantics should guide the resource plan.

## Syntax and data contract

Specify collect(engine="streaming") or collect(engine="in-memory") to make the experiment reproducible against the prepared version. sink_parquet writes the result artifact. Use explicit sorting for equality checks when output order is not otherwise guaranteed. A streamable custom batch function must preserve the result under valid batch partitions; it cannot secretly depend on the full dataset.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Compare engines and verify a sink

A thousand-row fixture is filtered and grouped. The two engine results must agree after the explicit sort, and a written Parquet result must agree with the collected frame. A Python sum independently checks the aggregate.

**Expected evidence:** Both engines and the artifact readback return the same five group totals.

```python
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


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Distinguish maps from reductions

The second case doubles each row and separately computes one global sum. This makes the output-grain difference visible without pretending that either shape alone establishes a memory guarantee.

**Expected evidence:** The map has 20 rows, the reduction 1 row; sum is 190 and doubled sum is 380.

```python
import polars as pl


def example_two():
    frame = pl.DataFrame({"x": range(20)})
    per_row = (
        frame.lazy().with_columns((pl.col("x") * 2).alias("twice")).collect(engine="streaming")
    )
    whole = frame.lazy().select(pl.col("x").sum().alias("total")).collect(engine="streaming")
    assert per_row.height == 20 and whole.height == 1
    assert whole.item() == 190 and per_row["twice"].sum() == 380
    return {"row_map_rows": 20, "reduction_rows": 1, "sum": 190}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Scale the fixture cautiously

Increase input size within a declared resource budget.

**Check:** The exact result still matches the independent formula.

**Hint:** Correctness must survive the scale change.


### 2. Change grouping cardinality

Use a nearly unique grouping key.

**Check:** The result has many more groups.

**Hint:** Batch processing can still accumulate group state.


### 3. Compare collect and sink

Write the same query directly to Parquet.

**Check:** Readback equals the collected result.

**Hint:** Inspect the actual output artifact.


### 4. Include a global sort

Add an ordered output requirement.

**Check:** The result obeys the declared order.

**Hint:** Ordering can require additional coordination and state.


### 5. Reject a false batch claim

Explain why subtracting a full-dataset mean is not independently streamable by arbitrary batches.

**Check:** The answer identifies dependence on global state.

**Hint:** Each batch has a different mean.


### 6. Report limitations

Write a capacity conclusion supported by this fixture.

**Check:** The conclusion is bounded to tested sizes and settings.

**Hint:** A successful process is a lower bound on what worked.


## Diagnose errors and misleading results

If a supposedly streaming job exhausts memory, inspect operator state, group cardinality, output materialization and accidental conversion into Python objects. If engines disagree, first compare schemas, ordering and floating tolerances before treating the difference as a speed result. Keep engine/version information with the observation.

## Transfer to independent work

Evaluate a query under an explicit engine and resource contract. Demonstrate equal logical results, inspect output materialization, and state which scalability questions remain unmeasured. This is the foundation for honest performance engineering.

## Primary references

- [Polars documentation: Streaming execution and bounded output](https://docs.pola.rs/user-guide/concepts/streaming/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-015`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
