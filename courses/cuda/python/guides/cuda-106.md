# cuda-106: A modern tile-based kernel DSL

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-074`, `cuda-076`, `cuda-079`, `cuda-085`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **create tile boundaries**, **state compiler requirements**, and **explain a resource tradeoff** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A thread-level model assigns scalar work to individual threads. A tile-level language describes a block of data and lets a compiler choose lower-level distribution and instructions. The abstraction can simplify matrix and reduction kernels, but layout, memory traffic, masks and numerical behavior still matter. Different DSL releases support different devices and operations.

Use a selected prepared Triton or CUDA tile implementation only after recording its compiler and architecture requirements. Compare the same mathematical operation against a library and the earlier thread-level reference. A masked tile must protect every invalid load and store at the boundary. This elective includes a CPU tiling model; the ordinary Python worker does not acquire a DSL compiler or GPU merely by opening the guide.



## Worked examples

### Worked example 1

A vector of 10 elements partitioned into tiles of 4 has tiles [0..3],[4..7],[8,9]. The last tile has two valid lanes and two masked lanes.

### Worked example 2

Changing tile size may improve reuse while increasing register pressure. The direction of the performance change must come from device evidence, not tile size alone.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
n, tile = 10, 4
blocks = [list(range(start, min(start + tile, n))) for start in range(0, n, tile)]
assert blocks == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
assert [i for block in blocks for i in block] == list(range(n))
print("CPU tile model:", blocks)
```

**Expected observation:** Three tiles cover ten elements exactly once.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Create tile boundaries

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **create tile boundaries** in the examples above.

### Exercise 2: Mask a final tile

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **mask a final tile** in the examples above.

### Exercise 3: Compare thread and tile abstractions

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **compare thread and tile abstractions** in the examples above.

### Exercise 4: State compiler requirements

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **state compiler requirements** in the examples above.

### Exercise 5: Design a library comparison

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design a library comparison** in the examples above.

### Exercise 6: Explain a resource tradeoff

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **explain a resource tradeoff** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Create tile boundaries".
2. Change one assumption in worked example 2 while preserving the declared contract: mask a final tile.
3. Trace the CPU program's variables before adding hardware behavior: compare thread and tile abstractions.
4. Draw producers, consumers and the exact operation boundary for the task "State compiler requirements".
5. Separate what the small fixture establishes from what the real runtime must show: design a library comparison.
6. Write a counterexample to an overbroad claim before you explain a resource tradeoff.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Create tile boundaries`. For the final claim use `Explain a resource tradeoff`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-106` using `courses/cuda/python/guides/cuda-106.md` and `courses/cuda/python/lessons/cuda-106.md`. Help me reason about A modern tile-based kernel DSL. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
