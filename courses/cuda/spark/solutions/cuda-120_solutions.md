# cuda-120: explained solutions

Compare with your [worksheet](../lessons/cuda-120.md) attempt.

## Exercise 1: Compute concurrent live memory

Add per-task live sets and shared state.

**Approach.** Compute concurrent live memory: three tasks at 2 GiB each plus 1 GiB shared workspace need `3*2 + 1 = 7` GiB, and four tasks need 9 GiB.

**Why it is correct here.** Tasks running at the same time each hold their live set, and the shared workspace is counted once. Peak demand is the sum at the point of greatest overlap.

**A plausible wrong approach.** Counting the shared workspace once per task gives 10 GiB for three tasks and wrongly rejects a configuration that fits.

**How to verify.** The reference asserts 7 and 9 and finds safe task counts `[1, 2, 3]` for an 8 GiB capacity.

## Exercise 2: Lower concurrency

Reduce simultaneous live demand.

**Approach.** Lower concurrency from four to three tasks to bring demand under the 8 GiB budget, since each task removed frees its 2 GiB live set.

**Why it is correct here.** Fewer simultaneous tasks reduce peak demand while each task's work is unchanged. The cost is less parallelism, which may lengthen the stage.

**A plausible wrong approach.** Raising batch size to finish faster increases per-task memory and makes the overflow worse. It may also push the job into heavier spilling, which slows the stage more than the larger batches speed it up.

**How to verify.** Run with three tasks and confirm that spill metrics fall and the stage completes without memory errors. Compare total stage time with the four-task run, since lower concurrency can still win once spilling stops.

## Exercise 3: Separate JVM and device pools

They are separate allocators and resources.

**Approach.** Separate JVM heap and device memory: Spark executor memory settings control the JVM heap on the host, while the plugin manages a separate GPU memory pool.

**Why it is correct here.** The two allocators serve different data and have different limits, so a GPU out-of-memory is not fixed by increasing the executor heap.

**A plausible wrong approach.** Raising `spark.executor.memory` after a GPU memory error adds host memory and leaves the device budget unchanged.

**How to verify.** Read the error message to see which allocator failed, and change the matching setting.

## Exercise 4: Budget spill disk

Use explicit disposable paths and capacity.

**Approach.** Budget spill disk with an explicit, disposable path and known capacity, since spilled batches are written to local storage.

**Why it is correct here.** Spill files consume disk space proportional to the spilled data. An unbounded spill can fill a shared disk.

**A plausible wrong approach.** Leaving spill on the default temporary directory of a small root volume risks filling it and affecting other processes.

**How to verify.** Configure the local directories, check free space before the run and record spill bytes after it.

## Exercise 5: Design safe batch changes

Bound rows and bytes before launch.

**Approach.** Design safe batch changes by bounding rows and bytes per batch before launch, such as limiting the target batch size, and change one setting at a time.

**Why it is correct here.** Batch size drives per-task memory. A bounded batch gives a predictable live set.

**A plausible wrong approach.** Doubling the batch size without a memory budget can turn a working job into an out-of-memory failure. The failure may appear only on the largest partitions, so small test inputs can pass while production data fails.

**How to verify.** Compute the per-task live set for the new batch size, compare with the budget, and then run.

## Exercise 6: Interpret successful but spilling execution

Completion is valid but performance and storage behavior need reporting.

**Approach.** Interpret a successful run with spills: the result is valid, but the report should state spill bytes and the added serialization and I/O time.

**Why it is correct here.** Spilling trades speed for completion. Reporting it explains slowdowns and warns that larger data may spill more.

**A plausible wrong approach.** Comparing only kernel times between a spilling run and a non-spilling run misses the end-to-end slowdown.

**How to verify.** Include spill bytes and stage time in the report next to the correctness check. Also record the spill path and peak disk use, since a later run with more data may exceed that capacity.

## Self-check answers

1. **What does a spill do?** It moves data to a slower tier so the query can progress under memory pressure, adding serialization and I/O cost.

2. **Why is comparing only kernel time misleading when spills occur?** Spills add end-to-end time outside the kernels, so the slowdown is invisible in kernel measurements.

3. **Why must memory experiments use bounded data?** Deliberately filling a shared device or disk can disrupt other users, so limits are set before running.

## Reference observation

One through three tasks fit the simplified budget; four do not.

Asserted by `courses/cuda/spark/references/cuda-120_cpu.py`.
