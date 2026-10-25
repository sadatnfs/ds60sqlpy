# cuda-084: CuPy raw kernels and the language boundary

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-009`, `cuda-011`, `cuda-073`, `cuda-082`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **derive expected affine output**, **reject noncontiguous input or support strides**, and **compare raw and library paths** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A raw kernel places CUDA C++ source inside a Python string and compiles it through the selected CuPy toolchain. Python controls allocation and launch; CUDA C++ controls thread-level arithmetic. The string does not gain automatic NumPy broadcasting, dtype promotion or stride support. A pointer signature and explicit length become a contract that the host must validate.

Use extern C to give the entrypoint a predictable symbol when appropriate, choose a narrow dtype contract, and guard the tail. The first invocation may compile and cache code, so separate compilation latency from warm execution. A raw kernel is attractive for a small fused operation, but a high-level CuPy expression remains a strong baseline. Existing single-source pads cannot be assumed to support arbitrary extension projects or external compiler flags.



## Worked examples

### Worked example 1

A float32 affine kernel computes `y[i] = 2*x[i] + 1`. For [-1,0,3] it returns [-1,1,7], and the host rejects a wrong dtype instead of reinterpreting it.

### Worked example 2

A launch for 257 elements using 128 threads requires three blocks. The last 127 valid-tail decisions belong in the kernel, even though the source is embedded in Python.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

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

### Exercise 1: Derive expected affine output

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **derive expected affine output** in the examples above.

### Exercise 2: Calculate a nonmultiple launch

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **calculate a nonmultiple launch** in the examples above.

### Exercise 3: Explain symbol lookup

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **explain symbol lookup** in the examples above.

### Exercise 4: Reject noncontiguous input or support strides

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **reject noncontiguous input or support strides** in the examples above.

### Exercise 5: Separate compile timing

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **separate compile timing** in the examples above.

### Exercise 6: Compare raw and library paths

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **compare raw and library paths** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Derive expected affine output".
2. Change one assumption in worked example 2 while preserving the declared contract: calculate a nonmultiple launch.
3. Trace the CPU program's variables before adding hardware behavior: explain symbol lookup.
4. Draw producers, consumers and the exact operation boundary for the task "Reject noncontiguous input or support strides".
5. Separate what the small fixture establishes from what the real runtime must show: separate compile timing.
6. Write a counterexample to an overbroad claim before you compare raw and library paths.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Derive expected affine output`. For the final claim use `Compare raw and library paths`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-084` using `courses/cuda/python/guides/cuda-084.md` and `courses/cuda/python/lessons/cuda-084.md`. Help me reason about CuPy raw kernels and the language boundary. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)
- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
