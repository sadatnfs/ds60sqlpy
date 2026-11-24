# cuda-074: One-dimensional indexing and tails

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-004`, `cuda-073`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute launch size for n=17**, **implement grid-stride coverage**, and **specify a sanitizer check** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A launch creates blocks containing threads. For one-dimensional indexing, global index equals block index times threads per block plus thread index. The last block often contains lanes beyond the input length. Guard every load and store that would otherwise access those lanes. Ceiling division creates enough blocks, while floor division silently omits a tail.

A grid-stride loop lets a bounded launch cover larger arrays: after processing index i, advance by the total number of launched threads. Every valid index should be visited exactly once for an elementwise operation. Test zero, one, block size minus one, block size, block size plus one and a nonmultiple. CPU scheduling models can prove the intended integer mapping, but cannot prove race freedom or GPU memory safety.



### Key terms

- **Global thread index:** The value `blockIdx.x * blockDim.x + threadIdx.x`, the unique element position assigned to a thread across the grid.
- **Tail guard:** A bounds check that stops threads whose index is past the last element when the grid is larger than the data.
- **Ceiling division:** The block count `(n + block - 1) // block`, which covers every element when n is not a multiple of the block size.
- **Grid-stride loop:** A loop in which each thread advances by the total thread count, letting a fixed grid process any input length.

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `n` | `10` |
| `block` | `4` |
| `blocks` | `3` |
| `visits` | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` |
| `strided` | `[0, 6, 12, 1, 7, 13, 2, 8, 3, 9, 4, 10, 5, 11]` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Optional NVIDIA CUDA lab

The **CuPy on NVIDIA CUDA** variant executes the actual operation with CuPy in the separately prepared `cuda-python` profile. It refuses a missing device instead of switching to CPU. Keep inputs bounded as supplied; inspect the device, synchronize and compare with the CPU reference. The profile must pass real host/device readiness checks. Successful syntax checking on a Mac is not GPU qualification.

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

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

**Trap to avoid:** Computing `n // block = 4` blocks is the floor-division mistake; the program runs without error and the last element is never written, so its output slot keeps whatever value was in the allocation.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Trace the last block

**Trap to avoid:** Assuming only one lane is out of range, or guarding with `i <= n`, lets index 17 through. That reads one element past the end, which may return a neighbor's data or trip a memory checker.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Test zero without launching

**Trap to avoid:** Clamping the grid to at least one block avoids the launch error but runs lanes whose guard is always false. That works, but it hides the empty case inside the kernel and still pays launch overhead for no work.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Implement grid-stride coverage

**Trap to avoid:** Advancing by `block_size` instead of the total thread count makes threads in different blocks visit the same indices. The output may still look right for idempotent writes, but accumulations double count.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Find floor-division data loss

**Trap to avoid:** Fixing it by launching `n // block + 1` blocks always adds a block even when `n` is a multiple of the block size. That is safe with a guard but launches an entire idle block for `n = 8`.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Specify a sanitizer check

**Trap to avoid:** Treating the passing CPU model as proof that the kernel is memory safe confuses the model of the formula with the code a compiler generated.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

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

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-074: One-dimensional indexing and tails.
Read courses/cuda/python/guides/cuda-074.md and courses/cuda/python/lessons/cuda-074.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
