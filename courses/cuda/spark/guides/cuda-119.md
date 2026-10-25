# cuda-119: GPU resources, executor ownership and task concurrency

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-114`, `cuda-115`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute resource-share slots**, **verify device addresses**, and **describe oversubscription failure** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Spark schedules executor and task resources, while the plugin manages how many tasks may actively use an executor's GPU. CPU task slots, fractional GPU resource requests and GPU admission concurrency are related but distinct controls. A fractional task resource amount is a scheduling share; it does not physically partition VRAM or make each task own an isolated fraction of the device.

Follow the selected plugin release's executor-to-GPU mapping and Spark resource discovery requirements. Use an explicitly prepared GPU discovery mechanism and verify assigned addresses. Raising concurrent GPU tasks may improve overlap but multiply live batches and memory pressure. A controlled experiment changes one concurrency setting, records resource allocation and observes actual completed-query throughput and memory.

## Resource accounting versus physical isolation

The executor GPU amount describes how much GPU resource Spark assigns to an executor. A task GPU amount describes how much of that assignment a task consumes for scheduling. CPU cores and `spark.task.cpus` impose another bound. The plugin's concurrent-GPU-task setting limits admission to GPU work inside the executor. These controls can all constrain one task without being interchangeable.

In a simplified configuration with one assigned GPU, four CPU slots and a task GPU amount of 0.25, resource accounting allows at most four tasks. A plugin GPU concurrency of two can allow only two of those tasks into GPU work simultaneously. Others may prepare input or wait, depending on implementation. This can improve overlap when preparation is expensive, but the gain is workload-specific.

A fractional GPU request does not partition device memory into equal private slices. Two admitted tasks can each allocate variable-size batches and workspaces, and their combined live set can exceed VRAM. Hardware partitioning technologies have distinct administration and support contracts and must not be inferred from Spark fractions. Measure memory alongside throughput when changing concurrency.

Before a real run, verify resource discovery and assigned device addresses inside the exact executor environment. The plugin's supported executor-to-GPU mapping is release-specific and currently documented separately from general Spark scheduling. Copying a generic Spark GPU configuration without checking plugin requirements can produce a valid-looking but unsupported setup. Keep all resource choices in the compatibility and experiment ledger.


## Worked examples

### Worked example 1

With an executor assigned one GPU and tasks requesting 0.25 GPU, resource accounting can admit up to four such tasks, subject to CPU slots and other limits. This is not four VRAM partitions.

### Worked example 2

A plugin concurrency limit of two can restrict active GPU work even when Spark has four runnable task slots. The two controls answer different scheduling questions.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
from fractions import Fraction

gpu = Fraction(1)
request = Fraction(1, 4)
slots = int(gpu / request)
plugin_limit = 2
active = min(slots, plugin_limit)
assert slots == 4 and active == 2
print("CPU resource model:", slots, "scheduled shares;", active, "GPU-active bound")
```

**Expected observation:** Four scheduling shares with a two-task plugin admission bound.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute resource-share slots

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute resource-share slots** in the examples above.

### Exercise 2: Compare CPU and GPU limits

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **compare CPU and GPU limits** in the examples above.

### Exercise 3: Explain VRAM nonpartitioning

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **explain VRAM nonpartitioning** in the examples above.

### Exercise 4: Verify device addresses

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **verify device addresses** in the examples above.

### Exercise 5: Design a concurrency experiment

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design a concurrency experiment** in the examples above.

### Exercise 6: Describe oversubscription failure

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **describe oversubscription failure** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute resource-share slots".
2. Change one assumption in worked example 2 while preserving the declared contract: compare CPU and GPU limits.
3. Trace the CPU program's variables before adding hardware behavior: explain VRAM nonpartitioning.
4. Draw producers, consumers and the exact operation boundary for the task "Verify device addresses".
5. Separate what the small fixture establishes from what the real runtime must show: design a concurrency experiment.
6. Write a counterexample to an overbroad claim before you describe oversubscription failure.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute resource-share slots`. For the final claim use `Describe oversubscription failure`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-119` using `courses/cuda/spark/guides/cuda-119.md` and `courses/cuda/spark/lessons/cuda-119.md`. Help me reason about GPU resources, executor ownership and task concurrency. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
