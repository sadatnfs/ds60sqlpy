# cuda-070: Memory pools, references and apparent leaks

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-068`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute live and reserved totals**, **explain why cache clearing is insufficient**, and **separate host RAM and VRAM** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A caching allocator distinguishes live allocations from reserved blocks. Releasing the last array reference can make a block reusable by the pool without returning it to the driver. Device-context overhead and library workspaces add further categories. A stable reserved total after repeated equal workloads can be normal. Growing live allocations after every step suggests retained tensors, outputs or computation graphs.

A pool can reduce allocation latency and fragmentation but cannot shrink the set of live tensors required by a model. Clearing unused cache blocks is not a repair for a workload whose live set exceeds memory. Measure at consistent synchronization points, account for delayed asynchronous frees, and avoid intentionally exhausting a shared GPU to demonstrate an OOM. A bounded allocation ledger teaches the same ownership distinction safely.



## Worked examples

### Worked example 1

An allocator reserves 1024 bytes, lends all 1024 to an array, then returns the array to its free list. Live bytes become zero while reserved bytes remain 1024.

### Worked example 2

Appending a fresh 1024-byte result to a Python list each step leaves every result live. After four steps live bytes are 4096; this is different from harmless pool reuse.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
reserved = 1024
live = 1024
live -= 1024
assert live == 0 and reserved == 1024
live += 1024
assert live <= reserved
retained = [1024 for _ in range(4)]
assert sum(retained) == 4096
print("CPU allocator model:", live, reserved, sum(retained))
```

**Expected observation:** Live 1024, reserved 1024, retained-output example 4096 bytes.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute live and reserved totals

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute live and reserved totals** in the examples above.

### Exercise 2: Reuse a free block

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **reuse a free block** in the examples above.

### Exercise 3: Diagnose a retained-output list

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **diagnose a retained-output list** in the examples above.

### Exercise 4: Explain why cache clearing is insufficient

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **explain why cache clearing is insufficient** in the examples above.

### Exercise 5: Design bounded snapshots

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design bounded snapshots** in the examples above.

### Exercise 6: Separate host RAM and VRAM

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **separate host RAM and VRAM** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute live and reserved totals".
2. Change one assumption in worked example 2 while preserving the declared contract: reuse a free block.
3. Trace the CPU program's variables before adding hardware behavior: diagnose a retained-output list.
4. Draw producers, consumers and the exact operation boundary for the task "Explain why cache clearing is insufficient".
5. Separate what the small fixture establishes from what the real runtime must show: design bounded snapshots.
6. Write a counterexample to an overbroad claim before you separate host RAM and VRAM.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute live and reserved totals`. For the final claim use `Separate host RAM and VRAM`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-070` using `courses/cuda/python/guides/cuda-070.md` and `courses/cuda/python/lessons/cuda-070.md`. Help me reason about Memory pools, references and apparent leaks. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
