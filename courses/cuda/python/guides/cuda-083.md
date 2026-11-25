# cuda-083: Python controls, CUDA executes

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-003`, `cuda-073`, `cuda-082`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Specify the kernel signature.
- Count allocation bytes.
- Classify compile versus launch errors.
- Design cleanup order.
- Explain ABI mismatch.
- Define release-pinned evidence.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-083_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-083_cpu.py
```

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

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-083.md) before opening hints.

### Exercise 1: Specify the kernel signature

**Trap to avoid:** Passing a plain Python `int` for `n` and letting the wrapper guess the width may package it as 64 bits. On some interfaces that shifts the following arguments or truncates the value.

### Exercise 2: Count allocation bytes

**Trap to avoid:** Sizing a buffer by element count alone, as if every element were one byte, under-allocates by the itemsize factor and lets the kernel write past the end.

### Exercise 3: Classify compile versus launch errors

**Trap to avoid:** Reporting compile success as working code treats the first stage as the whole contract. A module built for one architecture may still fail to load on another.

### Exercise 4: Design cleanup order

**Trap to avoid:** Releasing resources in reverse creation order without waiting looks tidy, but order of creation says nothing about device completion.

### Exercise 5: Explain ABI mismatch

**Trap to avoid:** Expecting a type error from the device is the mistake: device code has no runtime type information about its arguments.

### Exercise 6: Define release-pinned evidence

**Trap to avoid:** Recording only the Python package version omits the toolkit, driver and architecture, which are the usual causes of cross-machine failures.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. For each kernel parameter, write the element type behind the pointer and the exact width of each scalar.
2. Multiply the element count by the itemsize of the declared dtype and compare it with the allocated bytes.
3. Ask what each stage needs: compiling only needs source and target, while launching needs a compatible device.
4. List the resources in creation order, then ask what must complete before each one is released.
5. Pass a float64 buffer where float32 is expected and write down how the kernel would read the first element.
6. List every independently versioned component between your source and the device, and the target architecture.

## Common mistakes and self-check

The chapter's key mistake is passing arguments that do not match the compiled signature, such as a float64 allocation where the kernel expects float32, or a pointer where a 32-bit length belongs. The launch may not fail; it reads wrong bytes. Another mistake is checking only the launch status, which misses errors reported at completion. Fix both by validating dtype, size and argument layout in a small host wrapper, and by checking errors at submission and again after synchronization.

**Misconception:** Once a kernel compiles and the launch call returns without an error, the device has finished the computation correctly. **Correction:** A kernel launch is asynchronous: the call queues work on a stream and returns before the device runs it. Errors from an invalid memory access or a bad configuration can surface only at a later synchronization or copy, sometimes reported by an unrelated call. Compilation proves only that source was translated, possibly for an architecture this machine lacks. Treat compilation, submission, completion and readback equality as four separate checks, and synchronize before reading results on the host.

**Evidence limit:** The reference rejects storage too small for five float64 values in a CPU contract check. It does not load a driver, compile a module or launch anything, so binding behavior and release-specific API details need a prepared CUDA Python environment.

1. Why must compile success be recorded separately from launch success?
2. What does a launch need besides the compiled function?
3. Why use release-matched examples for CUDA Python?

Answers: [self-check answers](../solutions/cuda-083_solutions.md#self-check-answers).

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-083: Python controls, CUDA executes.
Read courses/cuda/python/guides/cuda-083.md and courses/cuda/python/lessons/cuda-083.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
