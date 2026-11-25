# cuda-119: GPU resources, executor ownership and task concurrency

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-114`, `cuda-115`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute resource-share slots.
- Compare CPU and GPU limits.
- Explain VRAM nonpartitioning.
- Verify device addresses.
- Design a concurrency experiment.
- Describe oversubscription failure.

## Mechanism and vocabulary

Spark schedules executor and task resources, while the plugin manages how many tasks may actively use an executor's GPU. CPU task slots, fractional GPU resource requests and GPU admission concurrency are related but distinct controls. A fractional task resource amount is a scheduling share; it does not physically partition VRAM or make each task own an isolated fraction of the device.

Follow the selected plugin release's executor-to-GPU mapping and Spark resource discovery requirements. Use an explicitly prepared GPU discovery mechanism and verify assigned addresses. Raising concurrent GPU tasks may improve overlap but multiply live batches and memory pressure. A controlled experiment changes one concurrency setting, records resource allocation and observes actual completed-query throughput and memory.

## Resource accounting versus physical isolation

The executor GPU amount describes how much GPU resource Spark assigns to an executor. A task GPU amount describes how much of that assignment a task consumes for scheduling. CPU cores and `spark.task.cpus` impose another bound. The plugin's concurrent-GPU-task setting limits admission to GPU work inside the executor. These controls can all constrain one task without being interchangeable.

In a simplified configuration with one assigned GPU, four CPU slots and a task GPU amount of 0.25, resource accounting allows at most four tasks. A plugin GPU concurrency of two can allow only two of those tasks into GPU work simultaneously. Others may prepare input or wait, depending on implementation. This can improve overlap when preparation is expensive, but the gain is workload-specific.

A fractional GPU request does not partition device memory into equal private slices. Two admitted tasks can each allocate variable-size batches and workspaces, and their combined live set can exceed VRAM. Hardware partitioning technologies have distinct administration and support contracts and must not be inferred from Spark fractions. Measure memory alongside throughput when changing concurrency.

Before a real run, verify resource discovery and assigned device addresses inside the exact executor environment. The plugin's supported executor-to-GPU mapping is release-specific and currently documented separately from general Spark scheduling. Copying a generic Spark GPU configuration without checking plugin requirements can produce a valid-looking but unsupported setup. Keep all resource choices in the compatibility and experiment ledger.


### Key terms

- **Executor:** A Spark JVM process that runs tasks and owns resources such as CPU cores and a GPU.
- **Task slot:** A unit of executor CPU capacity that allows one task to run.
- **Fractional GPU resource amount:** A per-task GPU request that sets a scheduling share but does not partition device memory.
- **GPU admission concurrency:** The plugin limit on how many tasks may actively use an executor's GPU at once.

## Worked examples

### Worked example 1

With an executor assigned one GPU and tasks requesting 0.25 GPU, resource accounting can admit up to four such tasks, subject to CPU slots and other limits. This is not four VRAM partitions.

### Worked example 2

A plugin concurrency limit of two can restrict active GPU work even when Spark has four runnable task slots. The two controls answer different scheduling questions.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-119_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-119_cpu.py
```

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `gpu` | `Fraction(1, 1)` |
| `request` | `Fraction(1, 4)` |
| `slots` | `4` |
| `plugin_limit` | `2` |
| `active` | `2` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-119.md) before opening hints.

### Exercise 1: Compute resource-share slots

**Trap to avoid:** Reading 0.25 as a quarter of the device's memory reserved for each task treats an admission count as a hardware partition, which Spark does not create.

### Exercise 2: Compare CPU and GPU limits

**Trap to avoid:** Tuning only the GPU amount and expecting four concurrent GPU tasks ignores the plugin limit, and the extra tasks hold CPU slots while waiting.

### Exercise 3: Explain VRAM nonpartitioning

**Trap to avoid:** Planning each task to have a quarter of device memory leads to out-of-memory errors when tasks use more than that share.

### Exercise 4: Verify device addresses

**Trap to avoid:** Assuming the default device assignment is correct on multi-GPU hosts risks oversubscribing one device.

### Exercise 5: Design a concurrency experiment

**Trap to avoid:** Changing concurrency and partition count together makes it impossible to tell which caused the change.

### Exercise 6: Describe oversubscription failure

**Trap to avoid:** Concluding from a successful small test that a concurrency setting is safe misses failures that appear with real data volumes.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Divide one assigned GPU by the per-task resource amount.
2. Find every limit that applies, such as CPU task slots, resource shares and plugin admission, and take the smallest.
3. Ask whether the scheduler reserves any memory on the device when it admits a task with a fractional amount.
4. Inspect which GPU addresses discovery reported and which ones each executor was assigned.
5. Change one concurrency setting and keep the query, partitions and data fixed.
6. Describe what happens to live batches and memory when too many tasks use the GPU at once.

## Common mistakes and self-check

A common mistake is reading a fractional GPU request such as 0.25 as a quarter of the device's memory. It is only a scheduling share; four admitted tasks still compete for the same VRAM. Another is assuming Spark's runnable task slots decide GPU concurrency, when the plugin's admission limit can be lower. Fix both by recording every resource control, verifying assigned device addresses and changing one concurrency setting at a time while observing throughput and memory.

**Evidence limit:** The reference computes four scheduling shares with a two-task admission bound. It does not run discovery or tasks, so actual assignment, memory pressure and throughput require a prepared GPU Spark cluster.

1. Which controls limit GPU task concurrency?
2. Why can raising concurrency fail without any syntax error?
3. What should resource discovery evidence show?

Answers: [self-check answers](../solutions/cuda-119_solutions.md#self-check-answers).

## Primary references

- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-119: GPU resources, executor ownership and task concurrency.
Read courses/cuda/spark/guides/cuda-119.md and courses/cuda/spark/lessons/cuda-119.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
