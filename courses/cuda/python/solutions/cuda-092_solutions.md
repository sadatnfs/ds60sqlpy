# cuda-092: explained solutions

Compare with your [worksheet](../lessons/cuda-092.md) attempt.

## Exercise 1: Compute timeline wall time

Use latest completion minus first start.

**Approach.** Compute wall time as latest completion minus earliest start: preparation runs 0 to 6 ms and GPU work 2 to 10 ms, so the step takes `10 - 0 = 10` ms.

**Why it is correct here.** The intervals overlap from 2 to 6 ms, so their durations cannot be added. Wall time is what the step costs end to end.

**A plausible wrong approach.** Summing durations, `6 + 8 = 14` ms, double counts the 4 ms overlap and overstates the step.

**How to verify.** The reference asserts `summed == 14` and `wall == 10`. Read both numbers off the trace to confirm.

## Exercise 2: Identify an overlap

Intervals sharing time overlap.

**Approach.** Find the overlap of the two intervals: `max(0, 2) = 2` to `min(6, 10) = 6`, so 4 ms of overlap.

**Why it is correct here.** Two intervals overlap when each starts before the other ends. Here CPU preparation for the next step runs while the GPU executes.

**A plausible wrong approach.** Treating events on different rows of the trace as sequential hides the concurrency that is already happening. The step then looks like it needs a faster GPU when the existing overlap is already working.

**How to verify.** Check `wall == summed - overlap`, which gives `14 - 4 = 10`, consistent with the reference.

## Exercise 3: Find a forced synchronization

Materializing a device scalar can wait.

**Approach.** Look for host reads of device scalars between kernels, such as `loss.item()` or `print(tensor)` each step, which appear in the trace as gaps followed by device-to-host copies.

**Why it is correct here.** Materializing a device value on the host requires the GPU to finish queued work first, which forces the host to wait and stops it from enqueueing further work.

**A plausible wrong approach.** Blaming the gaps on slow kernels leads to optimizing compute while the host dependency stays. Faster kernels only make the GPU wait longer for the next enqueue.

**How to verify.** Remove the per-step read in a test and confirm the gaps disappear. Then log aggregated values every N steps. The logged numbers must match the per-step values averaged over the same window.

## Exercise 4: Name profiler overhead

Detailed tracing changes work and memory.

**Approach.** Name the profiler's overhead: detailed tracing with stacks, memory recording and shape capture adds host work and memory, which changes timing.

**Why it is correct here.** A profiler observes by instrumenting. The trace shows relative structure well, but absolute numbers include instrumentation cost.

**A plausible wrong approach.** Quoting step times from a detailed profiler run as production numbers overstates the step time.

**How to verify.** Compare step times with profiling on and off. The difference estimates overhead. Also compare peak memory, since recording shapes and stacks keeps extra host and device allocations alive.

## Exercise 5: Propose one targeted change

Change only the suspected bottleneck.

**Approach.** Propose one targeted change, such as replacing per-step `loss.item()` with an aggregated log every 100 steps, and leave everything else fixed.

**Why it is correct here.** Changing one thing lets the trace before and after show its effect clearly. If the step time does not change, the hypothesis about the bottleneck was wrong, which is also useful evidence.

**A plausible wrong approach.** Applying several optimizations at once makes it impossible to tell which helped or which hurt. One change might help while another reintroduces a synchronization.

**How to verify.** Take a new trace and confirm the forced synchronizations are gone while losses remain the same.

## Exercise 6: Verify outside profiling

Rerun synchronized uninstrumented samples with equal outputs.

**Approach.** Verify the improvement outside the profiler: run synchronized, uninstrumented timings over many steps for both versions and confirm the outputs are equal.

**Why it is correct here.** Profiler numbers include overhead, so the final claim must come from clean measurements. Equal outputs confirm the change did not alter what the step computes.

**A plausible wrong approach.** Reporting the speedup measured under the profiler assumes overhead is equal in both versions. Removing host reads also removes instrumented events, so overhead itself changes.

**How to verify.** Report the median step time over a fixed number of steps after warm-up for both versions, with equal loss values.

## Self-check answers

1. **Why can summed event durations exceed wall time?** Events on the CPU and the GPU can run at the same time, so their durations overlap rather than add.

2. **Why is high GPU utilization not proof of useful work?** The device can be busy with wasteful copies or redundant kernels; utilization measures activity, not progress toward the result.

3. **What context must be kept with a saved trace?** The hardware, software versions and workload, because the same code can produce a very different trace elsewhere.

## Reference observation

Summed event durations 14 ms, complete interval 10 ms.

Asserted by `courses/cuda/python/references/cuda-092_cpu.py`.
