# cuda-077: Reduction, ordering and numerical error

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-006`, `cuda-074`, `cuda-076`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute a tree by hand**, **choose absolute and relative tolerance**, and **explain deterministic settings limits** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Parallel reduction changes the grouping of additions. Real-number addition is associative; finite-precision addition generally is not. A tree reduction can produce a different result from a left-to-right loop even when both are valid implementations. Test tolerances using scale and conditioning rather than requiring arbitrary bitwise identity. Distinguish a tolerable rounding difference from a missing tail element.

Reduction also changes the parallel ownership pattern. Threads first accumulate local partials, then combine within a block, then combine block results in a later stage. A single global atomic accumulator is simpler but can contend and has nondeterministic addition order. Use a higher-accuracy CPU sum where appropriate, test cancellation-heavy inputs, and document dtype and accumulation precision.



## Worked examples

### Worked example 1

For [1e16,1,-1e16], a naive left sum loses the one on common binary 64 arithmetic, while math.fsum preserves it. The input is intentionally cancellation-sensitive.

### Worked example 2

For [1,2,3,4,5], a padded pair tree produces 15. A faulty tree that ignores the fifth value produces 10, which is an indexing bug rather than rounding noise.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
import math

values = [1e16, 1.0, -1e16]
assert math.fsum(values) == 1.0
items = [1, 2, 3, 4, 5]
while len(items) > 1:
    items = [sum(items[i : i + 2]) for i in range(0, len(items), 2)]
assert items == [15]
print("CPU reduction reference:", math.fsum(values), items[0])
```

**Expected observation:** Accurate cancellation sum 1 and tail-preserving sum 15.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Optional NVIDIA CUDA lab

The **CuPy on NVIDIA CUDA** variant executes the actual operation with CuPy in the separately prepared `cuda-python` profile. It refuses a missing device instead of switching to CPU. Keep inputs bounded as supplied; inspect the device, synchronize and compare with the CPU reference. The profile must pass real host/device readiness checks. Successful syntax checking on a Mac is not GPU qualification.

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import math
import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

values = [1.0, 2.0, 3.0, 4.0, 5.0]
x = cp.asarray(values, dtype=cp.float64)
result = float(cp.sum(x).get())
assert math.isclose(result, math.fsum(values), rel_tol=1e-12, abs_tol=1e-12)
cp.cuda.get_current_stream().synchronize()
print("CUDA library reduction:", result, "; order-sensitive cases need a documented tolerance")
```

## Practice and transfer

### Exercise 1: Compute a tree by hand

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute a tree by hand** in the examples above.

### Exercise 2: Test the odd tail

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **test the odd tail** in the examples above.

### Exercise 3: Construct cancellation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **construct cancellation** in the examples above.

### Exercise 4: Choose absolute and relative tolerance

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **choose absolute and relative tolerance** in the examples above.

### Exercise 5: Compare atomics with staged reduction

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **compare atomics with staged reduction** in the examples above.

### Exercise 6: Explain deterministic settings limits

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **explain deterministic settings limits** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute a tree by hand".
2. Change one assumption in worked example 2 while preserving the declared contract: test the odd tail.
3. Trace the CPU program's variables before adding hardware behavior: construct cancellation.
4. Draw producers, consumers and the exact operation boundary for the task "Choose absolute and relative tolerance".
5. Separate what the small fixture establishes from what the real runtime must show: compare atomics with staged reduction.
6. Write a counterexample to an overbroad claim before you explain deterministic settings limits.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute a tree by hand`. For the final claim use `Explain deterministic settings limits`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-077` using `courses/cuda/python/guides/cuda-077.md` and `courses/cuda/python/lessons/cuda-077.md`. Help me reason about Reduction, ordering and numerical error. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
