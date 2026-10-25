# cuda-068: Array operations before custom kernels

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-066`, `cuda-067`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute centered columns**, **explain expanded-form cancellation**, and **choose a library baseline** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Broadcasting extends dimensions of size one logically, so a column mean can be subtracted from every row without constructing a full repeated matrix. A reduction consumes an axis; matrix multiplication combines contracted dimensions. These shape rules matter before choosing a backend. Express a correct reference using clear operations, then inspect whether intermediates and repeated launches dominate the useful work.

For squared distances, expanding \((x-y)^2\) gives \(x^2+y^2-2xy\). The expanded form avoids a full pairwise difference tensor but can lose relative accuracy when large nearly equal vectors cancel. A custom fused kernel can reduce temporary traffic, yet it creates maintenance, numerical and testing obligations. A mature library baseline is therefore both a correctness comparison and a performance competitor.



## Worked examples

### Worked example 1

Center rows [[1,3],[3,7]] by column means [2,5], producing [[-1,-2],[1,2]]. Each centered column sums to zero.

### Worked example 2

Distance between [1,2] and [4,6] is 25. Both direct differences and the expanded identity yield 25 for this small exact case; cancellation needs an additional adversarial test.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
rows = [[1.0, 3.0], [3.0, 7.0]]
means = [sum(row[c] for row in rows) / len(rows) for c in range(2)]
centered = [[x - m for x, m in zip(row, means, strict=True)] for row in rows]
assert centered == [[-1.0, -2.0], [1.0, 2.0]]
x, y = [1, 2], [4, 6]
distance = sum((a - b) ** 2 for a, b in zip(x, y, strict=True))
assert distance == 25
print("CPU array reference:", centered, distance)
```

**Expected observation:** Centered columns and distance 25.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Optional NVIDIA CUDA lab

The **CuPy on NVIDIA CUDA** variant executes the actual operation with CuPy in the separately prepared `cuda-python` profile. It refuses a missing device instead of switching to CPU. Keep inputs bounded as supplied; inspect the device, synchronize and compare with the CPU reference. The profile must pass real host/device readiness checks. Successful syntax checking on a Mac is not GPU qualification.

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.asarray([[1.0, 3.0], [3.0, 7.0]], dtype=cp.float32)
centered = x - cp.mean(x, axis=0)
cp.testing.assert_allclose(centered, cp.asarray([[-1, -2], [1, 2]], dtype=cp.float32))
cp.cuda.get_current_stream().synchronize()
print("CUDA centered features:", cp.asnumpy(centered).tolist())
```

## Practice and transfer

### Exercise 1: Compute centered columns

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute centered columns** in the examples above.

### Exercise 2: Add a constant feature

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **add a constant feature** in the examples above.

### Exercise 3: Implement distance directly

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **implement distance directly** in the examples above.

### Exercise 4: Explain expanded-form cancellation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **explain expanded-form cancellation** in the examples above.

### Exercise 5: Count a pairwise temporary

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **count a pairwise temporary** in the examples above.

### Exercise 6: Choose a library baseline

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **choose a library baseline** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute centered columns".
2. Change one assumption in worked example 2 while preserving the declared contract: add a constant feature.
3. Trace the CPU program's variables before adding hardware behavior: implement distance directly.
4. Draw producers, consumers and the exact operation boundary for the task "Explain expanded-form cancellation".
5. Separate what the small fixture establishes from what the real runtime must show: count a pairwise temporary.
6. Write a counterexample to an overbroad claim before you choose a library baseline.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute centered columns`. For the final claim use `Choose a library baseline`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-068` using `courses/cuda/python/guides/cuda-068.md` and `courses/cuda/python/lessons/cuda-068.md`. Help me reason about Array operations before custom kernels. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
