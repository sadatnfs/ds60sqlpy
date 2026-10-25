# cuda-082: Streams and events across library boundaries

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-067`, `cuda-071`, `cuda-081`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **draw the dependency graph**, **trace storage reuse**, and **explain why global synchronization can mask bugs** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A stream orders its submitted operations, but independent streams do not inherit every dependency you intend. A consumer on stream B must wait for the producer on stream A when it reads the produced buffer. An event records a point in one stream; a wait introduces a dependency without necessarily blocking the host. Synchronizing the entire device is a useful diagnostic but may destroy intended overlap.

Interop complicates the picture because libraries can have different current-stream conventions and allocator lifetimes. A correct pointer is insufficient if its write is still in flight or its storage is recycled before a consumer finishes. Draw the dependency graph first. Then use the documented stream-aware interchange and allocation recording mechanisms of the pinned libraries. Test a non-default stream to expose assumptions hidden by default execution.

## Build the dependency graph before writing the API calls

Consider two batches and two device streams. Stream A copies and transforms batch 0; stream B prepares batch 1. The host can submit both without waiting only when their allocations are distinct or their reuse is ordered. If both write the same staging buffer, the apparent overlap is a race. Double buffering introduces two owners and alternates them, but each buffer must still wait for its previous consumer before reuse.

An event is a marker in an ordered stream. Recording E after the transform means E becomes complete after earlier work in that stream. A wait for E in another stream places later consumer operations after that completion. This is different from waiting on the host: a host wait delays Python submission, while a stream wait can preserve useful overlap elsewhere. The resulting partial order is more precise than placing a device-wide synchronize after every statement.

The host can also accidentally serialize the graph. Calling `.item()`, `.get()` or `.numpy()` on a device result can require it to be ready on the host. Logging every intermediate scalar may insert repeated waits between kernels. This is not inherently wrong, but it changes the benchmark and can remove the overlap the program was supposed to measure. Aggregate bounded diagnostics where the application permits and preserve one explicit final output boundary.

Allocator reuse is the subtle companion to stream ordering. A library may know the allocation was used on its own stream but not that an external consumer still reads it. Use that library's documented external-stream or allocation-recording protocol. Do not solve this by keeping arbitrary global references forever: that trades a race for a memory leak. The acceptance test uses two non-default streams, repeated bounded inputs with distinct values, explicit producer/consumer ordering and a final comparison against the CPU oracle.


## Worked examples

### Worked example 1

Upload precedes transform, which precedes download. Independent preprocessing for the next batch may overlap only when it does not overwrite buffers still in use.

### Worked example 2

Producer A writes buffer X and records event E. Consumer B waits for E before reading X. The graph has an explicit edge even if host Python already returned from A.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
edges = [("upload", "transform"), ("transform", "download")]
order = ["upload", "transform", "download"]
positions = {name: i for i, name in enumerate(order)}
assert all(positions[a] < positions[b] for a, b in edges)
bad = ["download", "upload", "transform"]
assert not all(bad.index(a) < bad.index(b) for a, b in edges)
print("CPU dependency model: ordered pipeline accepted; premature download rejected")
```

**Expected observation:** Valid dependency order accepted; premature download rejected.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Draw the dependency graph

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **draw the dependency graph** in the examples above.

### Exercise 2: Locate a missing wait

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **locate a missing wait** in the examples above.

### Exercise 3: Separate host wait and stream wait

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **separate host wait and stream wait** in the examples above.

### Exercise 4: Trace storage reuse

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **trace storage reuse** in the examples above.

### Exercise 5: Design non-default stream test

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design non-default stream test** in the examples above.

### Exercise 6: Explain why global synchronization can mask bugs

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **explain why global synchronization can mask bugs** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Draw the dependency graph".
2. Change one assumption in worked example 2 while preserving the declared contract: locate a missing wait.
3. Trace the CPU program's variables before adding hardware behavior: separate host wait and stream wait.
4. Draw producers, consumers and the exact operation boundary for the task "Trace storage reuse".
5. Separate what the small fixture establishes from what the real runtime must show: design non-default stream test.
6. Write a counterexample to an overbroad claim before you explain why global synchronization can mask bugs.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Draw the dependency graph`. For the final claim use `Explain why global synchronization can mask bugs`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-082` using `courses/cuda/python/guides/cuda-082.md` and `courses/cuda/python/lessons/cuda-082.md`. Help me reason about Streams and events across library boundaries. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)
- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
