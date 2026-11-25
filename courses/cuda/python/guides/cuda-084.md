# cuda-084: CuPy raw kernels and the language boundary

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-009`, `cuda-011`, `cuda-073`, `cuda-082`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Derive expected affine output.
- Calculate a nonmultiple launch.
- Explain symbol lookup.
- Reject noncontiguous input or support strides.
- Separate compile timing.
- Compare raw and library paths.

## Mechanism and vocabulary

A raw kernel places CUDA C++ source inside a Python string and compiles it through the selected CuPy toolchain. Python controls allocation and launch; CUDA C++ controls thread-level arithmetic. The string does not gain automatic NumPy broadcasting, dtype promotion or stride support. A pointer signature and explicit length become a contract that the host must validate.

Use extern C to give the entrypoint a predictable symbol when appropriate, choose a narrow dtype contract, and guard the tail. The first invocation may compile and cache code, so separate compilation latency from warm execution. A raw kernel is attractive for a small fused operation, but a high-level CuPy expression remains a strong baseline. Existing single-source pads cannot be assumed to support arbitrary extension projects or external compiler flags.



### Key terms

- **RawKernel:** A CuPy object that compiles CUDA C source at run time and launches it with explicit grid, block and argument types.
- **extern "C" linkage:** A declaration that disables C++ name mangling so the kernel can be found by its plain name.
- **Contiguity requirement:** The assumption that array elements are densely packed, which raw pointer indexing needs to be correct.
- **Compilation cost:** The one-time time spent compiling kernel source, measured separately from launch and execution time.

## Worked examples

### Worked example 1

A float32 affine kernel computes `y[i] = 2*x[i] + 1`. For [-1,0,3] it returns [-1,1,7], and the host rejects a wrong dtype instead of reinterpreting it.

### Worked example 2

A launch for 257 elements using 128 threads requires three blocks. The last 127 valid-tail decisions belong in the kernel, even though the source is embedded in Python.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-084_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-084_cpu.py
```

```python
def affine(values):
    return [2 * x + 1 for x in values]


assert affine([-1, 0, 3]) == [-1, 1, 7]
n, threads = 257, 128
assert (n + threads - 1) // threads == 3
assert affine([]) == []
print("CPU raw-kernel oracle:", affine([-1, 0, 3]))
```

**Expected observation:** Affine result [-1,1,7], with three blocks for 257 elements.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `n` | `257` |
| `threads` | `128` |

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
extern "C" __global__ void affine(const float* x, float* y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = 2.0f * x[i] + 1.0f;
}
""",
    "affine",
)
x = cp.asarray([-1.0, 0.0, 3.0], dtype=cp.float32)
y = cp.empty_like(x)
kernel((1,), (128,), (x, y, cp.int32(x.size)))
cp.cuda.get_current_stream().synchronize()
cp.testing.assert_allclose(y, cp.asarray([-1.0, 1.0, 7.0], dtype=cp.float32))
print("CUDA raw affine:", cp.asnumpy(y).tolist())
```

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-084.md) before opening hints.

### Exercise 1: Derive expected affine output

**Trap to avoid:** Comparing against `2*(x+1)` by mistake gives `[0, 2, 8]` and suggests the kernel is wrong when the oracle is.

### Exercise 2: Calculate a nonmultiple launch

**Trap to avoid:** Using `257 // 128 = 2` blocks loses the final element silently, a bug invisible on sizes like 256.

### Exercise 3: Explain symbol lookup

**Trap to avoid:** Assuming a lookup error means the source failed to compile misdirects debugging to the kernel body.

### Exercise 4: Reject noncontiguous input or support strides

**Trap to avoid:** Silently calling `cupy.ascontiguousarray` inside the wrapper fixes correctness but hides a copy, and with in-place updates it writes to the copy instead of the caller's array.

### Exercise 5: Separate compile timing

**Trap to avoid:** Timing a single call and reporting it as kernel speed mostly measures the compiler.

### Exercise 6: Compare raw and library paths

**Trap to avoid:** Comparing a float32 raw kernel against a float64 library expression measures dtype rather than implementation.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Apply `2*x + 1` to each of `-1`, `0` and `3`.
2. Divide 257 by 128 and round up, then count how many lanes the last block holds beyond the data.
3. Ask what name the compiled module exports for the entry point and what `extern C` changes about it.
4. Decide whether the kernel will index with real strides or reject any input that is not contiguous.
5. Run the same kernel once before timing, then time repeated warm calls separately.
6. Compute the same affine result with a CuPy expression and compare outputs under one tolerance.

## Common mistakes and self-check

A common mistake is expecting a raw kernel to behave like a CuPy expression. The CUDA C++ inside the string has no broadcasting, dtype promotion or stride support; a float64 or sliced input is simply read as raw bytes. Another mistake is timing the first call, which includes compilation. Fix both by validating dtype, contiguity and length in Python before launching, guarding the tail in the kernel, and warming up before collecting steady-state samples.

**Evidence limit:** The reference checks the affine values `[-1, 1, 7]` and the three-block launch count with plain Python. It never compiles CUDA C++, so symbol lookup, compiler flags and warm execution time remain unverified.

1. Which side controls what in a raw kernel?
2. Why is a high-level CuPy expression still a strong baseline?
3. What happens on the first invocation of a raw kernel?

Answers: [self-check answers](../solutions/cuda-084_solutions.md#self-check-answers).

## Primary references

- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-084: CuPy raw kernels and the language boundary.
Read courses/cuda/python/guides/cuda-084.md and courses/cuda/python/lessons/cuda-084.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
