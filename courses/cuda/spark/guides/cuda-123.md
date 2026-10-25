# cuda-123: AQE, partition sizes and a fair benchmark

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-115`, `cuda-121`, `cuda-122`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **calculate partition averages**, **define cache policy**, and **separate estimated and observed speedup** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Adaptive Query Execution can coalesce partitions, change join strategy and respond to skew using runtime information. A GPU comparison must record the final executed plan, not only the initial configuration. Partition count changes task granularity, scheduler overhead, memory per task and available concurrency. There is no universal best count for every dataset and device.

Separate semantic smoke fixtures from performance datasets. Tiny data is excellent for correctness but often dominated by startup. Use the same input snapshots, query, output materialization, cache state and warmup policy for CPU and GPU comparisons. Report cold and warm runs, sample distributions and resource cost. Qualification estimates help select workloads; they are not measured speedups on the learner's hardware.



## Worked examples

### Worked example 1

One million rows split into 100 equal partitions averages 10000 rows each. Reducing to 10 partitions raises the average to 100000 and may increase per-task memory.

### Worked example 2

A warm GPU run reading cached data cannot fairly be compared with a cold CPU run downloading inputs. Label cache state or repeat under matched conditions.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
rows = 1_000_000
assert rows // 100 == 10000 and rows // 10 == 100000
runs = [{"backend": "CPU", "cache": "cold"}, {"backend": "GPU", "cache": "warm"}]
assert runs[0]["cache"] != runs[1]["cache"]
print("CPU benchmark worksheet: unmatched cache comparison rejected")
```

**Expected observation:** Partition averages 10000 and 100000; unmatched cache states rejected.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Calculate partition averages

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **calculate partition averages** in the examples above.

### Exercise 2: Explain skew beyond averages

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **explain skew beyond averages** in the examples above.

### Exercise 3: Capture final AQE plan

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **capture final AQE plan** in the examples above.

### Exercise 4: Define cache policy

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **define cache policy** in the examples above.

### Exercise 5: Choose semantic and performance fixtures

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **choose semantic and performance fixtures** in the examples above.

### Exercise 6: Separate estimated and observed speedup

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **separate estimated and observed speedup** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Calculate partition averages".
2. Change one assumption in worked example 2 while preserving the declared contract: explain skew beyond averages.
3. Trace the CPU program's variables before adding hardware behavior: capture final AQE plan.
4. Draw producers, consumers and the exact operation boundary for the task "Define cache policy".
5. Separate what the small fixture establishes from what the real runtime must show: choose semantic and performance fixtures.
6. Write a counterexample to an overbroad claim before you separate estimated and observed speedup.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Calculate partition averages`. For the final claim use `Separate estimated and observed speedup`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-123` using `courses/cuda/spark/guides/cuda-123.md` and `courses/cuda/spark/lessons/cuda-123.md`. Help me reason about AQE, partition sizes and a fair benchmark. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
