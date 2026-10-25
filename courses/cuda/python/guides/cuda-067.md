# cuda-067: Transfers have cost and lifetime

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-066`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **count bytes for ten iterations**, **explain pinned-memory lifetime**, and **identify an intentionally CPU-friendly workload** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A transfer pays fixed submission latency plus a size-dependent term. With payload B bytes and effective bandwidth W bytes per second, a useful first model is \(T=\ell+B/W\), where \(\ell\) is submission latency. This is a hypothesis for planning, not a benchmark. Small transfers often pay the fixed term repeatedly. Keeping intermediate arrays on device can save round trips even when the arithmetic expression does not change.

Asynchronous copying also creates an ownership obligation. The source must remain valid and unchanged until the copy finishes; the destination cannot be consumed before its dependency is satisfied. Pinned host memory can enable useful transfer overlap under supported conditions, but pinning every object consumes host resources. Count transfers before optimizing them and include serialization, packing and final output retrieval in end-to-end latency.



## Worked examples

### Worked example 1

Copying 100 rows separately at 10 microseconds submission cost spends at least 1 millisecond on submissions. One contiguous batch pays the submission term once.

### Worked example 2

Over K iterations, a transformation that copies input and output every iteration moves \(2KB\) bytes. Uploading once and downloading once moves \(2B\) bytes if all intermediates stay device-resident.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
size = 4096
iterations = 10
round_trip = 2 * size * iterations
resident = 2 * size
assert round_trip == 81920
assert resident == 8192
latency = 10e-6
bandwidth = 1e9
many = 100 * (latency + 40 / bandwidth)
one = latency + 4000 / bandwidth
assert many > one
print("CPU cost model:", round_trip, resident, "bytes")
```

**Expected observation:** 81920 versus 8192 modeled bytes; these are not measured timings.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Count bytes for ten iterations

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **count bytes for ten iterations** in the examples above.

### Exercise 2: Model a batched transfer

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **model a batched transfer** in the examples above.

### Exercise 3: Find premature source reuse

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **find premature source reuse** in the examples above.

### Exercise 4: Explain pinned-memory lifetime

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **explain pinned-memory lifetime** in the examples above.

### Exercise 5: Design an end-to-end timer

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design an end-to-end timer** in the examples above.

### Exercise 6: Identify an intentionally CPU-friendly workload

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **identify an intentionally CPU-friendly workload** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Count bytes for ten iterations".
2. Change one assumption in worked example 2 while preserving the declared contract: model a batched transfer.
3. Trace the CPU program's variables before adding hardware behavior: find premature source reuse.
4. Draw producers, consumers and the exact operation boundary for the task "Explain pinned-memory lifetime".
5. Separate what the small fixture establishes from what the real runtime must show: design an end-to-end timer.
6. Write a counterexample to an overbroad claim before you identify an intentionally CPU-friendly workload.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Count bytes for ten iterations`. For the final claim use `Identify an intentionally CPU-friendly workload`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-067` using `courses/cuda/python/guides/cuda-067.md` and `courses/cuda/python/lessons/cuda-067.md`. Help me reason about Transfers have cost and lifetime. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
