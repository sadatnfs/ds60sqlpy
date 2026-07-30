# Day 52 — Scalability with Dask and Chunked pandas

**Lesson ID:** `python-52` · **Level:** advanced · **Dependencies:** `production` · **Network:** offline

Dask partitions familiar array and DataFrame operations into a lazy task graph.
This lesson uses generated data and laptop-safe sizes to study execution
behavior; it is not a claim that distributed computation is always faster.

## Learning objectives

By the end of the lesson, you can:

- distinguish a lazy Dask collection from a computed pandas result;
- inspect and change DataFrame partitions;
- use `compute()` and `persist()` intentionally;
- aggregate a file in bounded pandas chunks; and
- compare runtime, memory, scheduler overhead, and code complexity.

## Prerequisites

- Complete `python-51` (advanced feature engineering).
- Be comfortable with pandas groupby and file I/O.
- Install the `production` dependency group during bootstrap.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Partition | Independently processed subset of a collection |
| Task graph | Deferred operations and their dependencies |
| Lazy evaluation | Builds a plan without executing it |
| `compute()` | Executes the graph and returns an in-memory result |
| `persist()` | Executes and retains partitions for reuse |
| Scheduler | Coordinates task execution |
| Shuffle | Redistributes rows across partitions; often expensive |
| Chunked processing | Explicitly reads and reduces bounded pieces, often with pandas |

Dask does not make memory limits disappear. A final `compute()` that produces a
huge pandas DataFrame still needs enough memory on the client.

## Worked example: generated, deterministic-scope data

```python
import dask.dataframe as dd

frame = dd.demo.make_timeseries(
    start="2000-01-01",
    end="2000-02-01",
    freq="1min",
    dtypes={"name": str, "id": int, "x": float, "y": float},
    partition_freq="7D",
)
lazy_mean = frame.groupby("name")["x"].mean()
print(frame.npartitions, lazy_mean)

result = lazy_mean.compute()
print(type(result), result.head())
```

Nothing expensive happens until an execution trigger such as `compute`,
`persist`, or a write. Inspect the task and expected output size before
triggering it.

## Learner exercises and progressive hints

1. Read a large local CSV with Dask and compute groupby aggregations.
2. Persist the DataFrame and compare repeated timings with and without
   persistence.
3. Implement the same reduction with `pandas.read_csv(..., chunksize=...)` and
   compare memory and elapsed time.

### Progressive hints

1. Generate a local CSV if you do not have one. Start small, validate against
   pandas, then scale until scheduling behavior is visible.
2. Persist helps only when reused. Time one warm-up/materialization and then the
   same two downstream aggregations; close any distributed client afterward.
3. Keep running sum and count per chunk so you never concatenate all chunks.
   Verify the final result against Dask within a tolerance.

The reference solution contains an illustrative `s3://...` placeholder. Do not
run it in the offline lesson. Replace it with a repository-local file or use the
notebook's generated frame.

### Additional mastery practice

Reason about partitions, task graphs, materialization, and associative reductions before scaling. Validate distributed results against a small exact baseline.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Task-graph tracing:** Build two aggregations from the same lazy Dask DataFrame, inspect their task graphs, and compare separate computes with one combined `dask.compute` call.
   **Progressive hint:** Building an expression does not read all data. Combining terminal computations can share upstream work without persisting the entire frame.
5. **Partition-skew diagnosis:** Create a group key where one value owns most rows. Measure partition sizes and groupby runtime, then propose repartitioning or algorithm changes.
   **Progressive hint:** A balanced row count before a shuffle does not guarantee balanced work after grouping; one hot key can become a straggler.
6. **Reducer correctness:** Implement a mergeable mean/variance state for chunks and prove it matches NumPy across different chunk boundaries, including an empty chunk.
   **Progressive hint:** A mean alone is not mergeable without support. Carry count, mean, and M2 (sum of squared deviations) using a stable combine formula.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- What type does a Dask groupby expression have before `compute()`?
- When can `persist()` make memory pressure worse?
- Why do many tiny partitions run slowly?
- Which reductions can be combined safely across independent chunks?

Expected behavior: the notebook's generated month has only a few partitions and
is safe on a normal laptop. Dask may be slower than pandas at this scale because
the scheduler adds overhead.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Response |
|---|---|---|
| No work seems to happen | Graph is still lazy | Call an intentional execution trigger |
| Client runs out of memory | Large result collected or persisted | Reduce before compute; inspect output size |
| Thousands of tiny tasks | Partitions are too small | Repartition to a sensible size |
| One task dominates | Skew or expensive shuffle | Inspect partitions and key distribution |
| Benchmark reverses on rerun | Cache/persist state differs | Declare cold/warm state and repeat |

The optional local dashboard at `http://127.0.0.1:8787` requires a local
`dask.distributed.Client`. It exposes task and memory behavior without sending
data over the Internet. Close the client to release processes.

## Next step

- Work in the [Day 52 learner notebook](../notebooks/day52_scalability_dask.ipynb).
- Then review the
  [Day 52 solution](../solutions/day52_scalability_dask/day52_solutions.md).
- Continue to [Day 53 — MLflow](day53_mlops_mlflow_experiment_tracking.md).
