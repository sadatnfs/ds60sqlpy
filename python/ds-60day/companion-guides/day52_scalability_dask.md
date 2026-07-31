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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 52 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — lazy task graphs, partitions, bounded reducers, and scale evidence

### The mental model

Dask DataFrame represents a logical plan split into pandas partitions.
Most operations are lazy: they build a task graph but do not read or
compute data until `compute` or `persist`. `persist` returns a new
collection backed by computed partitions; it is not an in-place flag.

Parallelism has overhead and memory cost. If data fits comfortably in
memory, pandas is often simpler and faster. Scalable reducers keep a
small associative state per chunk and combine states without loading
all rows. Partition size, skew, shuffles, and final-result size matter
more than merely importing Dask.

### Worked examples and syntax anatomy

- **lazy expression:** describes tasks and dependencies; inspect partitions/graph before execution.
- **`.compute()`:** executes the graph and materializes the result in local memory.
- **chunk state + combine:** keeps sufficient statistics such as sum/count rather than averaging chunk averages incorrectly.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — combine chunk sums and counts correctly

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
chunks = [[1.0, 2.0, 3.0], [100.0]]
states = [
    {"sum": sum(chunk), "count": len(chunk)}
    for chunk in chunks
]
total_sum = sum(state["sum"] for state in states)
total_count = sum(state["count"] for state in states)
correct_mean = total_sum / total_count
wrong_mean_of_means = sum(
    state["sum"] / state["count"] for state in states
) / len(states)
print({"correct": correct_mean, "wrong": wrong_mean_of_means})
assert correct_mean == 26.5 and wrong_mean_of_means != correct_mean
```

**Expected observation:** Unequal chunk sizes make an unweighted mean of chunk means wrong; sum and count compose exactly.

**Assumption to name:** Every valid value contributes once and missing-value rules are the same in every chunk.

### Focused example B — see a lazy Dask computation remain unevaluated

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
from dask import delayed

calls = []

@delayed
def record(value):
    calls.append(value)
    return value * 2

planned = record(21)
print({"before_compute_calls": list(calls), "planned_type": type(planned).__name__})
result = planned.compute(scheduler="single-threaded")
print({"after_compute_calls": list(calls), "result": result})
assert result == 42 and calls == [21]
```

**Expected observation:** Constructing the delayed object performs no work; `compute` executes the task exactly once.

**Assumption to name:** The single-threaded scheduler is chosen so this mechanics demonstration has deterministic local ordering.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define lazy task graphs, partitions, bounded reducers, and scale evidence in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Calling `compute()` after every transformation or persisting a collection larger than available memory.

**Debug it deliberately:** Inspect partition count/sizes, graph task count, shuffle boundaries, memory, and final result size; benchmark against pandas on the same data.

**Stop condition:** Do not claim scalability from elapsed time on one tiny demo or create partitions without a memory and overhead rationale.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Read a large local CSV with Dask and compute groupby aggregations.

**Verify:** Practice 1 — lazy task graphs, partitions, bounded reducers, and scale evidence — generate/read a named local CSV, print Dask partition count and groupby result, and assert keys/values match pandas within 1e-10 after deterministic sorting.

2. Persist the DataFrame and compare repeated timings with and without
   persistence.

**Verify:** Practice 2 — lazy task graphs, partitions, bounded reducers, and scale evidence — record at least three uncached and persisted repeated timings for the same aggregation, Dask graph/partition sizes, and result equality; close the local client and avoid claiming a speedup from one run.

3. Implement the same reduction with `pandas.read_csv(..., chunksize=...)` and
   compare memory and elapsed time.

**Verify:** Practice 3 — lazy task graphs, partitions, bounded reducers, and scale evidence — for identical CSV and aggregation, print pandas-chunked and Dask results, elapsed-time samples, and measured peak memory; assert sorted numeric outputs match within 1e-10.

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

**Verify:** Task-graph tracing — print task counts/graph keys for two separate aggregations and one combined dask.compute call; assert all numeric results match and report shared-prefix work without promising scheduler-specific task elimination.

5. **Partition-skew diagnosis:** Create a group key where one value owns most rows. Measure partition sizes and groupby runtime, then propose repartitioning or algorithm changes.
   **Progressive hint:** A balanced row count before a shuffle does not guarantee balanced work after grouping; one hot key can become a straggler.

**Verify:** Partition-skew diagnosis — print rows/bytes per partition, max-to-median skew ratio, dominant-key support, and repeated groupby timings before/after the chosen mitigation; assert outputs remain equal.

6. **Reducer correctness:** Implement a mergeable mean/variance state for chunks and prove it matches NumPy across different chunk boundaries, including an empty chunk.
   **Progressive hint:** A mean alone is not mergeable without support. Carry count, mean, and M2 (sum of squared deviations) using a stable combine formula.

**Verify:** Reducer correctness — test the mergeable state on empty, singleton, unequal, and reordered chunks; print count/mean/variance and assert agreement with NumPy within 1e-12 for every partitioning.

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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-52` — Day 52 — Scalability with Dask and Chunked pandas.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize lazy task graphs, partitions, bounded reducers, and scale evidence. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day52_scalability_dask.md`
- learner artifact: `python/ds-60day/notebooks/day52_scalability_dask.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-51`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
