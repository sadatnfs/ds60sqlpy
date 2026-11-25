# cuda-119: explained solutions

Compare with your [worksheet](../lessons/cuda-119.md) attempt.

## Exercise 1: Compute resource-share slots

One divided by 0.25 gives four accounting slots.

**Approach.** Compute resource-share slots: an executor with one GPU and tasks requesting `spark.task.resource.gpu.amount = 0.25` admits `1/0.25 = 4` tasks by GPU accounting.

**Why it is correct here.** Spark's resource scheduler treats the GPU as a divisible amount for admission. Four tasks of one quarter each exhaust the executor's one unit.

**A plausible wrong approach.** Reading 0.25 as a quarter of the device's memory reserved for each task treats an admission count as a hardware partition, which Spark does not create.

**How to verify.** The reference uses `Fraction` to compute `slots == 4` exactly. Check the executor's task count in the Spark UI while a stage runs.

## Exercise 2: Compare CPU and GPU limits

The effective bound includes all constraints.

**Approach.** Combine CPU and GPU limits: the effective number of concurrent tasks is the minimum of GPU shares, executor cores divided by cores per task, and the plugin's concurrent GPU task limit; with a plugin limit of 2 the active bound is `min(4, 2) = 2`.

**Why it is correct here.** Each control gates a different resource. Spark may run four tasks, but the plugin lets only two use the GPU at once, so the others wait inside the plugin.

**A plausible wrong approach.** Tuning only the GPU amount and expecting four concurrent GPU tasks ignores the plugin limit, and the extra tasks hold CPU slots while waiting.

**How to verify.** The reference asserts `active == 2`. Record each setting and compare with observed concurrent GPU tasks in plugin metrics.

## Exercise 3: Explain VRAM nonpartitioning

Scheduling fractions do not reserve fixed memory slices.

**Approach.** Explain that fractional GPU amounts do not partition VRAM: four tasks sharing one GPU allocate from the same device memory pool as their work demands.

**Why it is correct here.** Scheduling shares limit how many tasks start, but each task's memory use depends on its batch and operators. One large task can use most of the memory.

**A plausible wrong approach.** Planning each task to have a quarter of device memory leads to out-of-memory errors when tasks use more than that share.

**How to verify.** Monitor device memory during a stage with several tasks and observe that usage varies by task rather than splitting evenly.

## Exercise 4: Verify device addresses

Inspect explicit discovery and assignment.

**Approach.** Verify device addresses: check that each executor discovers its GPUs through the configured discovery script and that task resource info lists the assigned address.

**Why it is correct here.** Explicit discovery prevents two executors on a host from both using GPU 0 while another GPU sits idle.

**A plausible wrong approach.** Assuming the default device assignment is correct on multi-GPU hosts risks oversubscribing one device.

**How to verify.** Log `TaskContext.get().resources()['gpu'].addresses` in a small job and confirm addresses are distinct across executors on the same host.

## Exercise 5: Design a concurrency experiment

Hold query partitions and data fixed.

**Approach.** Design a concurrency experiment that varies only the task concurrency setting while holding the query, partition count and data fixed.

**Why it is correct here.** Partition count and data size both affect stage time, so they must stay constant for differences to be attributed to concurrency.

**A plausible wrong approach.** Changing concurrency and partition count together makes it impossible to tell which caused the change.

**How to verify.** Record settings and stage metrics for each run, and confirm the outputs match across runs.

## Exercise 6: Describe oversubscription failure

Too many live tasks can spill or fail without any syntax error.

**Approach.** Describe oversubscription failure: too many live tasks on one GPU can exhaust device memory, causing spills or task failures without any syntax or configuration error.

**Why it is correct here.** Memory demand appears only at runtime, so a configuration that looks valid can fail on larger data.

**A plausible wrong approach.** Concluding from a successful small test that a concurrency setting is safe misses failures that appear with real data volumes.

**How to verify.** Increase concurrency on a representative dataset and watch spill metrics and task failures to find the safe bound.

## Self-check answers

1. **Which controls limit GPU task concurrency?** CPU task slots, fractional GPU resource requests and the plugin's GPU admission concurrency, which together set the effective bound.

2. **Why can raising concurrency fail without any syntax error?** More active tasks multiply live batches, so memory pressure can cause spills or failures at run time.

3. **What should resource discovery evidence show?** The GPU addresses that were discovered and the address assigned to each executor.

## Reference observation

Four scheduling shares with a two-task plugin admission bound.

Asserted by `courses/cuda/spark/references/cuda-119_cpu.py`.
