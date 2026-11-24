# cuda-120: Memory pools, batch sizing and bounded spills

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-118`, `cuda-119`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute concurrent live memory**, **budget spill disk**, and **interpret successful but spilling execution** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

GPU Spark uses device allocations for columnar batches, intermediate operators and workspaces, with host memory and disk potentially involved in spill behavior. The JVM heap is only one memory category. Reducing executor heap does not directly create VRAM, and increasing GPU task concurrency can raise simultaneous live memory even when each task fits alone.

A spill moves data to a slower tier to preserve progress under pressure. It is an operational behavior to measure, not an automatic failure or a free capacity extension. Record device, pinned host, pageable host and spill-disk budgets separately. Use small deterministic datasets for semantics and bounded representative data for performance; never deliberately fill a shared device or disk. Check plugin-specific memory settings against the pinned release.



### Key terms

- **Device memory pool:** A pooled GPU allocator, such as the RAPIDS Memory Manager, that serves columnar batches and workspaces.
- **Spill:** Moving data to a slower tier such as host memory or disk to preserve progress under memory pressure.
- **JVM heap:** Executor memory managed by Java, which is separate from GPU device memory.
- **Batch size target:** The configured columnar batch size, which trades per-batch overhead against peak device memory.

## Worked examples

### Worked example 1

Three active tasks each needing 2 GiB plus 1 GiB shared workspace require an illustrative 7 GiB live budget. Four tasks require 9 GiB and exceed an 8 GiB budget.

### Worked example 2

A spill can allow completion while adding serialization and I/O cost. Comparing only kernel time misses the resulting end-to-end slowdown.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
per_task, shared, capacity = 2, 1, 8
assert 3 * per_task + shared == 7
assert 4 * per_task + shared == 9
safe = [tasks for tasks in range(1, 5) if tasks * per_task + shared <= capacity]
assert safe == [1, 2, 3]
print("CPU memory budget:", safe, "safe task counts in the model")
```

**Expected observation:** One through three tasks fit the simplified budget; four do not.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `per_task` | `2` |
| `shared` | `1` |
| `capacity` | `8` |
| `safe` | `[1, 2, 3]` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute concurrent live memory

**Trap to avoid:** Counting the shared workspace once per task gives 10 GiB for three tasks and wrongly rejects a configuration that fits.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Lower concurrency

**Trap to avoid:** Raising batch size to finish faster increases per-task memory and makes the overflow worse. It may also push the job into heavier spilling, which slows the stage more than the larger batches speed it up.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Separate JVM and device pools

**Trap to avoid:** Raising `spark.executor.memory` after a GPU memory error adds host memory and leaves the device budget unchanged.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Budget spill disk

**Trap to avoid:** Leaving spill on the default temporary directory of a small root volume risks filling it and affecting other processes.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Design safe batch changes

**Trap to avoid:** Doubling the batch size without a memory budget can turn a working job into an out-of-memory failure. The failure may appear only on the largest partitions, so small test inputs can pass while production data fails.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Interpret successful but spilling execution

**Trap to avoid:** Comparing only kernel times between a spilling run and a non-spilling run misses the end-to-end slowdown.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute concurrent live memory".
2. Change one assumption in worked example 2 while preserving the declared contract: lower concurrency.
3. Trace the CPU program's variables before adding hardware behavior: separate JVM and device pools.
4. Draw producers, consumers and the exact operation boundary for the task "Budget spill disk".
5. Separate what the small fixture establishes from what the real runtime must show: design safe batch changes.
6. Write a counterexample to an overbroad claim before you interpret successful but spilling execution.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute concurrent live memory`. For the final claim use `Interpret successful but spilling execution`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-120: Memory pools, batch sizing and bounded spills.
Read courses/cuda/spark/guides/cuda-120.md and courses/cuda/spark/lessons/cuda-120.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
