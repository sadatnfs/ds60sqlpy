# cuda-120: Memory pools, batch sizing and bounded spills

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-118`, `cuda-119`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute concurrent live memory.
- Lower concurrency.
- Separate JVM and device pools.
- Budget spill disk.
- Design safe batch changes.
- Interpret successful but spilling execution.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-120_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-120_cpu.py
```

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

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-120.md) before opening hints.

### Exercise 1: Compute concurrent live memory

**Trap to avoid:** Counting the shared workspace once per task gives 10 GiB for three tasks and wrongly rejects a configuration that fits.

### Exercise 2: Lower concurrency

**Trap to avoid:** Raising batch size to finish faster increases per-task memory and makes the overflow worse. It may also push the job into heavier spilling, which slows the stage more than the larger batches speed it up.

### Exercise 3: Separate JVM and device pools

**Trap to avoid:** Raising `spark.executor.memory` after a GPU memory error adds host memory and leaves the device budget unchanged.

### Exercise 4: Budget spill disk

**Trap to avoid:** Leaving spill on the default temporary directory of a small root volume risks filling it and affecting other processes.

### Exercise 5: Design safe batch changes

**Trap to avoid:** Doubling the batch size without a memory budget can turn a working job into an out-of-memory failure. The failure may appear only on the largest partitions, so small test inputs can pass while production data fails.

### Exercise 6: Interpret successful but spilling execution

**Trap to avoid:** Comparing only kernel times between a spilling run and a non-spilling run misses the end-to-end slowdown.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Add each active task's live set and the shared workspace once.
2. Recompute the total with one task fewer and compare it with the budget.
3. Ask whether shrinking the JVM heap frees anything on the GPU.
4. Choose an explicit disposable path for spill files and set a capacity limit for it.
5. Fix row and byte bounds for a batch before launching the run.
6. Ask what a completed but spilling run proves and what it still needs reported.

## Common mistakes and self-check

A common mistake is tuning the JVM heap to fix GPU memory pressure. They are separate allocators, so reducing heap creates no VRAM. Another mistake is raising GPU task concurrency because each task fits alone; three tasks fit a modeled 8 GiB budget, but four need 9 GiB. A third is treating spill as failure or as free capacity. Fix these by budgeting device, pinned host, pageable host and spill disk separately and lowering concurrency when live demand exceeds the budget.

**Misconception:** Pinned host memory is an unlimited fast staging area, so a larger pinned pool is always better. **Correction:** Pinned memory is page-locked host memory that the operating system cannot swap out, so a large pool takes RAM away from the JVM, Python workers and other processes on the host. It speeds transfers and spills to host memory, but it is a fixed budget like device memory. Size it in the same ledger as the heap, the device pool and spill disk, and change it in bounded steps.

**Evidence limit:** The reference fits one to three tasks into an illustrative 8 GiB budget and rejects four. Real live sets, workspaces and spill thresholds depend on the query and the plugin release, so they must be observed on a prepared host with bounded data.

1. What does a spill do?
2. Why is comparing only kernel time misleading when spills occur?
3. Why must memory experiments use bounded data?

Answers: [self-check answers](../solutions/cuda-120_solutions.md#self-check-answers).

## Primary references

- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-120: Memory pools, batch sizing and bounded spills.
Read courses/cuda/spark/guides/cuda-120.md and courses/cuda/spark/lessons/cuda-120.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
