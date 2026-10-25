# cuda-066: Shape, dtype, stride and layout are a contract

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-065`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **calculate offset (1,1)**, **find the contiguous-only bug**, and **design layout contract tests** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Shape describes logical coordinates; strides describe the byte displacement when one coordinate increases by one. A contiguous row-major matrix with three float32 columns has strides (12, 4). A slice selecting alternate columns changes the last stride without necessarily copying storage. Its shape alone cannot tell a raw kernel how to find the next element.

An address is the allocation base plus view offset plus the sum of index times stride. Dtype determines interpretation and element width, not just a display label. A kernel accepting only contiguous float32 data should validate those conditions or explicitly pack a copy and account for it. Supporting arbitrary strides requires a different indexing contract. Never reinterpret float64 bytes as float32 because the element count happens to match.



## Worked examples

### Worked example 1

For a 2 by 3 float32 array, coordinate (1, 2) is \(1\times12+2\times4=20\) bytes from the base. The allocation occupies 24 bytes.

### Worked example 2

A column slice choosing columns 0 and 2 has shape (2, 2), strides (12, 8) and a 16-byte logical payload. Its covered storage spans 24 bytes; logical bytes and storage span differ.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
def offset(indices, strides):
    return sum(i * s for i, s in zip(indices, strides, strict=True))


assert offset((1, 2), (12, 4)) == 20
assert offset((1, 1), (12, 8)) == 20
assert offset((2, 1), (4, 12)) == 20
print("CPU layout model:", offset((1, 2), (12, 4)), "bytes")
```

**Expected observation:** All three views address byte offset 20.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Optional NVIDIA CUDA lab

The **CuPy on NVIDIA CUDA** variant executes the actual operation with CuPy in the separately prepared `cuda-python` profile. It refuses a missing device instead of switching to CPU. Keep inputs bounded as supplied; inspect the device, synchronize and compare with the CPU reference. The profile must pass real host/device readiness checks. Successful syntax checking on a Mac is not GPU qualification.

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.arange(6, dtype=cp.float32).reshape(2, 3)
view = x[:, ::2]
assert view.shape == (2, 2)
assert view.strides == (12, 8)
cp.testing.assert_array_equal(view, cp.asarray([[0, 2], [3, 5]], dtype=cp.float32))
cp.cuda.get_current_stream().synchronize()
print("CUDA layout:", view.shape, view.strides, cp.asnumpy(view).tolist())
```

## Practice and transfer

### Exercise 1: Calculate offset (1,1)

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **calculate offset (1,1)** in the examples above.

### Exercise 2: Change dtype to float64

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **change dtype to float64** in the examples above.

### Exercise 3: Describe a transposed view

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **describe a transposed view** in the examples above.

### Exercise 4: Find the contiguous-only bug

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **find the contiguous-only bug** in the examples above.

### Exercise 5: Specify negative-stride support

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **specify negative-stride support** in the examples above.

### Exercise 6: Design layout contract tests

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **design layout contract tests** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Calculate offset (1,1)".
2. Change one assumption in worked example 2 while preserving the declared contract: change dtype to float64.
3. Trace the CPU program's variables before adding hardware behavior: describe a transposed view.
4. Draw producers, consumers and the exact operation boundary for the task "Find the contiguous-only bug".
5. Separate what the small fixture establishes from what the real runtime must show: specify negative-stride support.
6. Write a counterexample to an overbroad claim before you design layout contract tests.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Calculate offset (1,1)`. For the final claim use `Design layout contract tests`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-066` using `courses/cuda/python/guides/cuda-066.md` and `courses/cuda/python/lessons/cuda-066.md`. Help me reason about Shape, dtype, stride and layout are a contract. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
