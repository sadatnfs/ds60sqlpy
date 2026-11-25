# cuda-074: One-dimensional indexing and tails

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-004`, `cuda-073`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute launch size for n=17.
- Trace the last block.
- Test zero without launching.
- Implement grid-stride coverage.
- Find floor-division data loss.
- Specify a sanitizer check.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-074_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-074_cpu.py
```

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

## Optional NVIDIA CUDA lab

**CuPy on NVIDIA CUDA** needs the `cuda-python` profile; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

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

Record each attempt in the [worksheet](../lessons/cuda-074.md) before opening hints.

### Exercise 1: Compute launch size for n=17

**Trap to avoid:** Computing `n // block = 4` blocks is the floor-division mistake; the program runs without error and the last element is never written, so its output slot keeps whatever value was in the allocation.

### Exercise 2: Trace the last block

**Trap to avoid:** Assuming only one lane is out of range, or guarding with `i <= n`, lets index 17 through. That reads one element past the end, which may return a neighbor's data or trip a memory checker.

### Exercise 3: Test zero without launching

**Trap to avoid:** Clamping the grid to at least one block avoids the launch error but runs lanes whose guard is always false. That works, but it hides the empty case inside the kernel and still pays launch overhead for no work.

### Exercise 4: Implement grid-stride coverage

**Trap to avoid:** Advancing by `block_size` instead of the total thread count makes threads in different blocks visit the same indices. The output may still look right for idempotent writes, but accumulations double count.

### Exercise 5: Find floor-division data loss

**Trap to avoid:** Fixing it by launching `n // block + 1` blocks always adds a block even when `n` is a multiple of the block size. That is safe with a guard but launches an entire idle block for `n = 8`.

### Exercise 6: Specify a sanitizer check

**Trap to avoid:** Treating the passing CPU model as proof that the kernel is memory safe confuses the model of the formula with the code a compiler generated.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Divide 17 by the block size and round up, not down, then count the launched lanes.
2. List the global indices of the last block and mark which ones exceed the valid range.
3. Ask what the output for an empty input is and whether any launch is needed to produce it.
4. After handling index i, how far must a thread advance so that no other thread repeats its work?
5. Compute 17 divided by 4 with floor division and list the indices no block covers.
6. Decide which tool can observe an out-of-bounds device access that a CPU model never performs.

## Common mistakes and self-check

The most common mistake is sizing the grid with floor division, which silently omits the final partial block, or launching with ceiling division but forgetting the bounds guard so lanes 10 and 11 in worked example 1 touch memory past the buffer. Fix both by using ceiling division for the block count and guarding every load and store with the input length, then test zero, one, block size minus one, block size, block size plus one and a nonmultiple.

**Evidence limit:** The reference proves the integer mapping visits every valid index exactly once. It cannot prove race freedom, memory safety or correct guards in a real kernel; those need execution under a supported memory checker on a device.

1. How is the global index computed in one-dimensional indexing?
2. Why does a grid-stride loop help with large arrays?
3. Which input sizes belong in an indexing test set?

Answers: [self-check answers](../solutions/cuda-074_solutions.md#self-check-answers).

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-074: One-dimensional indexing and tails.
Read courses/cuda/python/guides/cuda-074.md and courses/cuda/python/lessons/cuda-074.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
