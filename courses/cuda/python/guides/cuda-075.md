# cuda-075: Two-dimensional indexing and images

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-074`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **trace a rectangular tile**, **find in-place stencil contamination**, and **explain row and column tail guards** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

An image has coordinates, channel conventions and storage layout. Map thread x to columns and thread y to rows only after defining that contract. A row-major scalar image uses offset `row * width + column`. A rectangular block launch requires independent checks for row and column, because the input dimensions may have different tails. Multiplying both dimensions by the same bound accidentally accepts invalid coordinates.

Stencil operations read neighbors, so boundary policy is part of correctness: zero padding, clamp, reflect and valid-only output produce different results. Read from an immutable input and write to a separate output unless a proven algorithm allows in-place updates. A CPU loop is useful because its coordinate meanings are visible. Do not infer coalescing or performance from that loop's execution time.



## Worked examples

### Worked example 1

For a 2 by 3 image, row 1 column 2 maps to flat offset 5. Swapping row and column changes the address and can escape the allocation.

### Worked example 2

A horizontal three-point average with clamped borders maps [3,6,9] to [4,6,8]. Zero padding would produce [3,6,5], a different documented operation.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
values = [3, 6, 9]
clamped = [
    (values[max(0, i - 1)] + values[i] + values[min(len(values) - 1, i + 1)]) / 3
    for i in range(len(values))
]
assert clamped == [4, 6, 8]
assert 1 * 3 + 2 == 5
print("CPU image reference:", clamped)
```

**Expected observation:** Clamped horizontal average [4, 6, 8].

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Trace a rectangular tile

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **trace a rectangular tile** in the examples above.

### Exercise 2: Calculate flat offsets

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **calculate flat offsets** in the examples above.

### Exercise 3: Change clamp to zero padding

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **change clamp to zero padding** in the examples above.

### Exercise 4: Find in-place stencil contamination

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **find in-place stencil contamination** in the examples above.

### Exercise 5: Test width one

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **test width one** in the examples above.

### Exercise 6: Explain row and column tail guards

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **explain row and column tail guards** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Trace a rectangular tile".
2. Change one assumption in worked example 2 while preserving the declared contract: calculate flat offsets.
3. Trace the CPU program's variables before adding hardware behavior: change clamp to zero padding.
4. Draw producers, consumers and the exact operation boundary for the task "Find in-place stencil contamination".
5. Separate what the small fixture establishes from what the real runtime must show: test width one.
6. Write a counterexample to an overbroad claim before you explain row and column tail guards.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Trace a rectangular tile`. For the final claim use `Explain row and column tail guards`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-075` using `courses/cuda/python/guides/cuda-075.md` and `courses/cuda/python/lessons/cuda-075.md`. Help me reason about Two-dimensional indexing and images. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
