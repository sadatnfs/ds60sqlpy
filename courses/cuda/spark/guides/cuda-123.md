# cuda-123: AQE, partition sizes and a fair benchmark

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-115`, `cuda-121`, `cuda-122`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Calculate partition averages.
- Explain skew beyond averages.
- Capture final AQE plan.
- Define cache policy.
- Choose semantic and performance fixtures.
- Separate estimated and observed speedup.

## Mechanism and vocabulary

Adaptive Query Execution can coalesce partitions, change join strategy and respond to skew using runtime information. A GPU comparison must record the final executed plan, not only the initial configuration. Partition count changes task granularity, scheduler overhead, memory per task and available concurrency. There is no universal best count for every dataset and device.

Separate semantic smoke fixtures from performance datasets. Tiny data is excellent for correctness but often dominated by startup. Use the same input snapshots, query, output materialization, cache state and warmup policy for CPU and GPU comparisons. Report cold and warm runs, sample distributions and resource cost. Qualification estimates help select workloads; they are not measured speedups on the learner's hardware.



### Key terms

- **Partition coalescing:** AQE merging small shuffle partitions after measuring their actual sizes.
- **Skew join handling:** AQE splitting oversized partitions so one key does not dominate a join stage.
- **Partition count:** The number of partitions, which sets task granularity, scheduler overhead and memory per task.
- **Startup-dominated run:** A run on tiny data whose time is mostly fixed setup, which is unsuitable for performance claims.

## Worked examples

### Worked example 1

One million rows split into 100 equal partitions averages 10000 rows each. Reducing to 10 partitions raises the average to 100000 and may increase per-task memory.

### Worked example 2

A warm GPU run reading cached data cannot fairly be compared with a cold CPU run downloading inputs. Label cache state or repeat under matched conditions.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-123_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-123_cpu.py
```

```python
rows = 1_000_000
assert rows // 100 == 10000 and rows // 10 == 100000
runs = [{"backend": "CPU", "cache": "cold"}, {"backend": "GPU", "cache": "warm"}]
assert runs[0]["cache"] != runs[1]["cache"]
print("CPU benchmark worksheet: unmatched cache comparison rejected")
```

**Expected observation:** Partition averages 10000 and 100000; unmatched cache states rejected.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rows` | `1000000` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-123.md) before opening hints.

### Exercise 1: Calculate partition averages

**Trap to avoid:** Reducing partitions to cut scheduling overhead without checking per-task memory can turn a working job into a spilling one.

### Exercise 2: Explain skew beyond averages

**Trap to avoid:** Reporting only the average leaves skew invisible. Adding partitions does not fix skew either, because a hot key still lands in one partition however many there are.

### Exercise 3: Capture final AQE plan

**Trap to avoid:** Reporting partition counts from the pre-execution plan can describe a configuration AQE changed. Coalescing may reduce 200 shuffle partitions to a handful, which changes per-task memory considerably.

### Exercise 4: Define cache policy

**Trap to avoid:** Comparing those runs reports a speedup partly caused by the cache, as the reference rejects for unmatched cache states.

### Exercise 5: Choose semantic and performance fixtures

**Trap to avoid:** Reporting performance from the tiny correctness fixture gives timings that say nothing about production scale. At a few rows, Spark job scheduling dominates and both backends look the same, or the GPU looks slower.

### Exercise 6: Separate estimated and observed speedup

**Trap to avoid:** Writing an estimated 3 times speedup into a report as achieved presents unverified data as fact. Readers then plan hardware purchases or migrations around a number nobody measured.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Divide the row count by the partition count for both settings.
2. Ask what an average hides when one partition is much larger than the rest, and which numbers reveal it.
3. Trigger an action first, then read the plan the completed query actually used.
4. Decide whether both runs start with cold caches or warm caches, and record which.
5. Use a tiny fixture to check correctness and a separate representative dataset to measure speed.
6. Ask whether a qualification tool's estimate has been confirmed by running the workload on your hardware.

## Common mistakes and self-check

A common mistake is comparing a warm GPU run on cached data with a cold CPU run that downloads its inputs, then reporting the ratio as a speedup. Another is timing tiny correctness fixtures, where startup dominates, or citing a qualification estimate as a measured result. Fix these by using the same input snapshot, query, output materialization, cache state and warmup policy on both backends, reporting cold and warm distributions separately and recording the executed plan and partition sizes for every measured run.

**Misconception:** The configured partition count is the number of partitions the stage runs with. **Correction:** With AQE enabled, Spark can coalesce small shuffle partitions after a stage completes and split skewed ones in joins, so the executed partition count can differ from the configured value. Per-task memory and concurrency follow the executed partitions. Read partition counts and sizes from the completed query's stage metrics and report them with the timing, and confirm that CPU and GPU runs used comparable plans.

**Evidence limit:** The reference computes partition averages of 10000 and 100000 and rejects unmatched cache states. It runs no queries, so AQE decisions, per-task memory and actual speedups must be observed with representative data on the target cluster.

1. What can Adaptive Query Execution change at run time?
2. Is there a best partition count for all workloads?
3. Why keep semantic fixtures separate from performance datasets?

Answers: [self-check answers](../solutions/cuda-123_solutions.md#self-check-answers).

## Primary references

- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-123: AQE, partition sizes and a fair benchmark.
Read courses/cuda/spark/guides/cuda-123.md and courses/cuda/spark/lessons/cuda-123.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
