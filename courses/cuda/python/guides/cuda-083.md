# cuda-083: Python controls, CUDA executes

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-003`, `cuda-073`, `cuda-082`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **specify the kernel signature**, **design cleanup order**, and **define release-pinned evidence** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Python host code can select a device, allocate memory, prepare compiled code and submit a kernel. These are resource-management operations, distinct from device arithmetic. Low-level CUDA bindings expose handles, status values and byte counts that higher-level arrays normally hide. A kernel launch also needs argument layout, grid/block geometry and a stream, all matched to the compiled function signature.

Keep beginners on a small reviewed host wrapper before exposing every binding. The wrapper validates input, owns resources and checks both submission errors and later completion errors. CUDA Python components are independently versioned; use release-matched examples rather than copying a moving development API. For this chapter the CPU contract lab checks argument and lifetime reasoning; a prepared external CUDA Python driver lab requires its own version ledger.



### Key terms

- **Low-level binding:** A thin Python interface that exposes driver or runtime API calls nearly one to one.
- **Handle:** An opaque value identifying a context, module, stream or allocation that must be created and destroyed explicitly.
- **Status code:** The result value every low-level call returns, which must be checked because errors do not raise exceptions automatically.
- **Application binary interface (ABI):** The binary contract, including symbol names, calling conventions and data layouts, that compiled components must agree on.

## Worked examples

### Worked example 1

A kernel expecting float32 input plus a 32-bit length cannot safely receive a float64 allocation plus a pointer where an integer belongs. Values need ABI-correct representation.

### Worked example 2

Compilation success is recorded separately from launch success and readback equality. A program can compile for a device architecture absent on the current machine.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
def validate_contract(count, itemsize, allocated):
    if count < 0 or itemsize <= 0 or allocated < count * itemsize:
        raise ValueError("invalid buffer contract")


validate_contract(5, 4, 20)
try:
    validate_contract(5, 8, 20)
except ValueError:
    print("CPU ABI model: insufficient float64 storage rejected")
else:
    raise AssertionError("expected rejection")
```

**Expected observation:** Insufficient storage for five float64 values is rejected.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Specify the kernel signature

**Trap to avoid:** Passing a plain Python `int` for `n` and letting the wrapper guess the width may package it as 64 bits. On some interfaces that shifts the following arguments or truncates the value.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Count allocation bytes

**Trap to avoid:** Sizing a buffer by element count alone, as if every element were one byte, under-allocates by the itemsize factor and lets the kernel write past the end.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Classify compile versus launch errors

**Trap to avoid:** Reporting compile success as working code treats the first stage as the whole contract. A module built for one architecture may still fail to load on another.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Design cleanup order

**Trap to avoid:** Releasing resources in reverse creation order without waiting looks tidy, but order of creation says nothing about device completion.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Explain ABI mismatch

**Trap to avoid:** Expecting a type error from the device is the mistake: device code has no runtime type information about its arguments.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Define release-pinned evidence

**Trap to avoid:** Recording only the Python package version omits the toolkit, driver and architecture, which are the usual causes of cross-machine failures.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Specify the kernel signature".
2. Change one assumption in worked example 2 while preserving the declared contract: count allocation bytes.
3. Trace the CPU program's variables before adding hardware behavior: classify compile versus launch errors.
4. Draw producers, consumers and the exact operation boundary for the task "Design cleanup order".
5. Separate what the small fixture establishes from what the real runtime must show: explain ABI mismatch.
6. Write a counterexample to an overbroad claim before you define release-pinned evidence.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Specify the kernel signature`. For the final claim use `Define release-pinned evidence`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)
- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-083: Python controls, CUDA executes.
Read courses/cuda/python/guides/cuda-083.md and courses/cuda/python/lessons/cuda-083.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
