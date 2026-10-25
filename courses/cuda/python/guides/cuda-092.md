# cuda-092: Profiling a complete training step

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-071`, `cuda-088`, `cuda-089`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute timeline wall time**, **name profiler overhead**, and **verify outside profiling** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A profiler records events and dependencies, but a table of operator totals is not itself the critical path. CPU preparation, copies, kernels, synchronization and logging may overlap. Summing all event durations can exceed wall time when events run concurrently. Instrumentation also adds overhead, especially with shapes, stacks or memory capture enabled.

PyTorch profiler activities and named ranges make forward, backward and update visible; TensorFlow Profiler adds graph and input-pipeline views. Capture a short bounded schedule after warmup, inspect a timeline, then test one hypothesis with ordinary timing. Preserve a trace's hardware, software and workload context. A busy GPU can spend time on wasteful copies or redundant kernels, so utilization alone is not useful-work evidence.



## Worked examples

### Worked example 1

CPU preparation from 0 to 6 ms overlaps GPU work from 2 to 10 ms. The complete interval is 10 ms, not 14 ms obtained by summing durations.

### Worked example 2

A trace with repeated host scalar reads between kernels can reveal forced synchronization. Replacing per-step logging with bounded aggregated reporting changes the host dependency path.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
events = [("prepare", 0, 6), ("gpu", 2, 10)]
summed = sum(end - start for _, start, end in events)
wall = max(end for _, _, end in events) - min(start for _, start, _ in events)
assert summed == 14 and wall == 10
print("CPU timeline analysis:", summed, wall)
```

**Expected observation:** Summed event durations 14 ms, complete interval 10 ms.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Capture a bounded torch.profiler schedule with CPU and CUDA activities when available, add named ranges, then verify the hypothesis with ordinary synchronized timing.

### TensorFlow

Capture a short TensorFlow Profiler trace using the prepared external tooling. Use input-pipeline and device views together, then repeat without profiling overhead.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Compute timeline wall time

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute timeline wall time** in the examples above.

### Exercise 2: Identify an overlap

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **identify an overlap** in the examples above.

### Exercise 3: Find a forced synchronization

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **find a forced synchronization** in the examples above.

### Exercise 4: Name profiler overhead

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **name profiler overhead** in the examples above.

### Exercise 5: Propose one targeted change

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **propose one targeted change** in the examples above.

### Exercise 6: Verify outside profiling

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **verify outside profiling** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute timeline wall time".
2. Change one assumption in worked example 2 while preserving the declared contract: identify an overlap.
3. Trace the CPU program's variables before adding hardware behavior: find a forced synchronization.
4. Draw producers, consumers and the exact operation boundary for the task "Name profiler overhead".
5. Separate what the small fixture establishes from what the real runtime must show: propose one targeted change.
6. Write a counterexample to an overbroad claim before you verify outside profiling.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute timeline wall time`. For the final claim use `Verify outside profiling`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-092` using `courses/cuda/python/guides/cuda-092.md` and `courses/cuda/python/lessons/cuda-092.md`. Help me reason about Profiling a complete training step. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
