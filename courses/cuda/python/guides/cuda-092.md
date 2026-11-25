# cuda-092: Profiling a complete training step

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-071`, `cuda-088`, `cuda-089`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute timeline wall time.
- Identify an overlap.
- Find a forced synchronization.
- Name profiler overhead.
- Propose one targeted change.
- Verify outside profiling.

## Mechanism and vocabulary

A profiler records events and dependencies, but a table of operator totals is not itself the critical path. CPU preparation, copies, kernels, synchronization and logging may overlap. Summing all event durations can exceed wall time when events run concurrently. Instrumentation also adds overhead, especially with shapes, stacks or memory capture enabled.

PyTorch profiler activities and named ranges make forward, backward and update visible; TensorFlow Profiler adds graph and input-pipeline views. Capture a short bounded schedule after warmup, inspect a timeline, then test one hypothesis with ordinary timing. Preserve a trace's hardware, software and workload context. A busy GPU can spend time on wasteful copies or redundant kernels, so utilization alone is not useful-work evidence.



### Key terms

- **Profiler trace:** A timeline of host calls, kernel launches, copies and synchronizations recorded during a bounded run.
- **Critical path:** The longest chain of dependent work in the timeline, which determines total elapsed time.
- **Forced synchronization:** A host wait inserted by operations such as `.item()` or printing, which appears as an idle gap in the trace.
- **Profiler overhead:** Extra time introduced by instrumentation, so profiled timings should not be reported as performance.

## Worked examples

### Worked example 1

CPU preparation from 0 to 6 ms overlaps GPU work from 2 to 10 ms. The complete interval is 10 ms, not 14 ms obtained by summing durations.

### Worked example 2

A trace with repeated host scalar reads between kernels can reveal forced synchronization. Replacing per-step logging with bounded aggregated reporting changes the host dependency path.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-092_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-092_cpu.py
```

```python
events = [("prepare", 0, 6), ("gpu", 2, 10)]
summed = sum(end - start for _, start, end in events)
wall = max(end for _, _, end in events) - min(start for _, start, _ in events)
assert summed == 14 and wall == 10
print("CPU timeline analysis:", summed, wall)
```

**Expected observation:** Summed event durations 14 ms, complete interval 10 ms.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `events` | `[('prepare', 0, 6), ('gpu', 2, 10)]` |
| `summed` | `14` |
| `wall` | `10` |

## Equal framework lanes

### PyTorch

Capture a bounded torch.profiler schedule with CPU and CUDA activities when available, add named ranges, then verify the hypothesis with ordinary synchronized timing.

### TensorFlow

Capture a short TensorFlow Profiler trace using the prepared external tooling. Use input-pipeline and device views together, then repeat without profiling overhead.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-092.md) before opening hints.

### Exercise 1: Compute timeline wall time

**Trap to avoid:** Summing durations, `6 + 8 = 14` ms, double counts the 4 ms overlap and overstates the step.

### Exercise 2: Identify an overlap

**Trap to avoid:** Treating events on different rows of the trace as sequential hides the concurrency that is already happening. The step then looks like it needs a faster GPU when the existing overlap is already working.

### Exercise 3: Find a forced synchronization

**Trap to avoid:** Blaming the gaps on slow kernels leads to optimizing compute while the host dependency stays. Faster kernels only make the GPU wait longer for the next enqueue.

### Exercise 4: Name profiler overhead

**Trap to avoid:** Quoting step times from a detailed profiler run as production numbers overstates the step time.

### Exercise 5: Propose one targeted change

**Trap to avoid:** Applying several optimizations at once makes it impossible to tell which helped or which hurt. One change might help while another reintroduces a synchronization.

### Exercise 6: Verify outside profiling

**Trap to avoid:** Reporting the speedup measured under the profiler assumes overhead is equal in both versions. Removing host reads also removes instrumented events, so overhead itself changes.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Take the latest end time and subtract the earliest start time.
2. List the time ranges where both the CPU and GPU intervals are active.
3. Look for a host line that turns a device value into a Python number between kernels.
4. Ask what recording shapes, stacks and memory adds to every event.
5. Pick the single bottleneck the timeline suggests and change only that.
6. Rerun without the profiler, synchronize before reading the clock and check the outputs still match.

## Common mistakes and self-check

A frequent mistake is adding up operator durations from a profiler table and calling the result step time. When CPU preparation and GPU kernels overlap, the sum exceeds wall time: 14 ms instead of 10 ms in worked example 1. Another mistake is trusting GPU utilization, since a busy device can be running redundant copies. Fix both by reading the timeline for the critical path, testing one hypothesis at a time and confirming with uninstrumented, synchronized timing.

**Evidence limit:** The reference computes a 14 ms event sum against a 10 ms interval from given timestamps. It does not capture a trace, so real overlap, synchronization points and profiler overhead must come from a bounded profile on the target system.

1. Why can summed event durations exceed wall time?
2. Why is high GPU utilization not proof of useful work?
3. What context must be kept with a saved trace?

Answers: [self-check answers](../solutions/cuda-092_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-092: Profiling a complete training step.
Read courses/cuda/python/guides/cuda-092.md and courses/cuda/python/lessons/cuda-092.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
