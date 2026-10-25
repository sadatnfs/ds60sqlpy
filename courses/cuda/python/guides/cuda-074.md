# cuda-074: One-dimensional indexing and tails

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-004`, `cuda-073`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute launch size for n=17**, **implement grid-stride coverage**, and **specify a sanitizer check** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A launch creates blocks containing threads. For one-dimensional indexing, global index equals block index times threads per block plus thread index. The last block often contains lanes beyond the input length. Guard every load and store that would otherwise access those lanes. Ceiling division creates enough blocks, while floor division silently omits a tail.

A grid-stride loop lets a bounded launch cover larger arrays: after processing index i, advance by the total number of launched threads. Every valid index should be visited exactly once for an elementwise operation. Test zero, one, block size minus one, block size, block size plus one and a nonmultiple. CPU scheduling models can prove the intended integer mapping, but cannot prove race freedom or GPU memory safety.



## Worked examples

### Worked example 1

For n=10 and block size 4, three blocks launch 12 lanes. Indices 0 through 9 are valid, while 10 and 11 must not access the buffer.

### Worked example 2

With six total threads and n=14, thread zero visits 0,6,12 and thread one visits 1,7,13. The union contains every valid index exactly once.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
n, block = 10, 4
blocks = (n + block - 1) // block
visits = [b * block + t for b in range(blocks) for t in range(block) if b * block + t < n]
assert visits == list(range(n))
strided = [i for t in range(6) for i in range(t, 14, 6)]
assert sorted(strided) == list(range(14))
print("CPU indexing model:", visits)
```

**Expected observation:** Every valid index appears exactly once.

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

kernel = cp.RawKernel(
    r"""
extern "C" __global__ void twice(const float* x, float* y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = 2.0f * x[i];
}
""",
    "twice",
)
for n in [0, 1, 127, 128, 129, 257]:
    x = cp.arange(n, dtype=cp.float32)
    y = cp.empty_like(x)
    if n:
        kernel(((n + 127) // 128,), (128,), (x, y, cp.int32(n)))
    cp.cuda.get_current_stream().synchronize()
    cp.testing.assert_array_equal(y, 2 * x)
print("CUDA tail tests passed for zero, singleton and nonmultiples")
```

## Practice and transfer

### Exercise 1: Compute launch size for n=17

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute launch size for n=17** in the examples above.

### Exercise 2: Trace the last block

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **trace the last block** in the examples above.

### Exercise 3: Test zero without launching

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **test zero without launching** in the examples above.

### Exercise 4: Implement grid-stride coverage

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **implement grid-stride coverage** in the examples above.

### Exercise 5: Find floor-division data loss

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **find floor-division data loss** in the examples above.

### Exercise 6: Specify a sanitizer check

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **specify a sanitizer check** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute launch size for n=17".
2. Change one assumption in worked example 2 while preserving the declared contract: trace the last block.
3. Trace the CPU program's variables before adding hardware behavior: test zero without launching.
4. Draw producers, consumers and the exact operation boundary for the task "Implement grid-stride coverage".
5. Separate what the small fixture establishes from what the real runtime must show: find floor-division data loss.
6. Write a counterexample to an overbroad claim before you specify a sanitizer check.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute launch size for n=17`. For the final claim use `Specify a sanitizer check`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-074` using `courses/cuda/python/guides/cuda-074.md` and `courses/cuda/python/lessons/cuda-074.md`. Help me reason about One-dimensional indexing and tails. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
