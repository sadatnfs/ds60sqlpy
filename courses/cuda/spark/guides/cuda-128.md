# cuda-128: When GPU Spark is the wrong tool

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-123`, `cuda-126`, `cuda-127`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute end-to-end tradeoff**, **include operational cost**, and **write an evidence-based recommendation** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A good acceleration decision includes a credible no-change outcome. Tiny data, unsupported expressions, expensive transfers, external I/O, severe skew or a memory-constrained device can make CPU Spark or a single-process dataframe the better choice. Distributed scheduling overhead can dominate a workload that fits comfortably in one local process. GPU capability is one input to architecture, not a requirement to use it.

Compare total completion time, resource cost, operational complexity and output quality under actual constraints. Maintain a CPU fallback installation separately from plugin operator fallback. Revisit the decision when data size, workload mix or hardware changes. The final review should identify the smallest supported system that solves the problem and the evidence that would justify expanding it.



## Worked examples

### Worked example 1

A local CPU dataframe finishes a tiny analysis in 0.1 seconds while Spark startup takes several seconds. No kernel speedup can erase startup for a one-off job without changing the execution model.

### Worked example 2

A GPU query saves 30 seconds of compute but adds 40 seconds of transfers and conversions. The complete application loses 10 seconds despite faster arithmetic.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
saved_compute, added_transfer = 30, 40
net = added_transfer - saved_compute
assert net == 10
candidates = {"local_cpu": 0.1, "spark_startup_only": 3.0}
assert candidates["local_cpu"] < candidates["spark_startup_only"]
print("CPU architecture decision: GPU candidate adds", net, "seconds")
```

**Expected observation:** GPU candidate adds 10 modeled seconds end to end.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute end-to-end tradeoff

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute end-to-end tradeoff** in the examples above.

### Exercise 2: Choose a tiny-data tool

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **choose a tiny-data tool** in the examples above.

### Exercise 3: Separate setup and steady state

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **separate setup and steady state** in the examples above.

### Exercise 4: Include operational cost

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **include operational cost** in the examples above.

### Exercise 5: Define a reevaluation trigger

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **define a reevaluation trigger** in the examples above.

### Exercise 6: Write an evidence-based recommendation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **write an evidence-based recommendation** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute end-to-end tradeoff".
2. Change one assumption in worked example 2 while preserving the declared contract: choose a tiny-data tool.
3. Trace the CPU program's variables before adding hardware behavior: separate setup and steady state.
4. Draw producers, consumers and the exact operation boundary for the task "Include operational cost".
5. Separate what the small fixture establishes from what the real runtime must show: define a reevaluation trigger.
6. Write a counterexample to an overbroad claim before you write an evidence-based recommendation.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute end-to-end tradeoff`. For the final claim use `Write an evidence-based recommendation`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-128` using `courses/cuda/spark/guides/cuda-128.md` and `courses/cuda/spark/lessons/cuda-128.md`. Help me reason about When GPU Spark is the wrong tool. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
