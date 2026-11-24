# cuda-013: Explicit device allocation and transfer

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-010`, `cuda-012`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement checked device allocation and transfers that preserve guard values and clean up after an injected failure.

Work through *Explicit device allocation and transfer* with the concrete cases below. Finish with this evidence:
unchanged guard values, correct output, checked statuses and cleanup after an injected host-side failure. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

cudaMalloc requests a number of bytes and returns a device allocation handle through a pointer argument. For n float elements, calculate n*sizeof(float), checking multiplication bounds for externally supplied sizes. cudaMemcpy also takes bytes and an explicit direction in the simple runtime API. The input owner must remain alive until the transfer finishes, and the device output must remain allocated until its final consumer completes. Host-to-device transfer supplies input; device-to-host transfer produces an observable result. A pointer is not a container with a length field, so the surrounding program must preserve size and lifetime metadata.

### Key terms

- **cudaMalloc:** The runtime call that reserves a number of bytes in device global memory and returns a device pointer.
- **cudaMemcpy:** A runtime copy between host and device memory that takes a byte count and an explicit direction.
- **Device pointer:** An address that is valid for device access and that ordinary host code must not dereference.
- **Guard value:** A known sentinel placed beyond the valid range so that an out-of-bounds write becomes detectable.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-013_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-013_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Copy \([2,4,6,8]\) as float32. Four elements require 16 bytes. A request for four bytes copies only one float. Zero-initialized test data can hide that error, so use distinct nonzero entries and validate the entire result after the round trip.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
storage = [-99, 1, 2, 3, -99]
for i in range(1, 4):
    storage[i] *= 2
assert storage == [-99, 2, 4, 6, -99]
assert 4 * 4 == 16
print({"guarded_output": storage, "four_float32_bytes": 16})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'guarded_output': [-99, 2, 4, 6, -99], 'four_float32_bytes': 16}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Place sentinel values around a three-element target: \([-99,1,2,3,-99]\). Transform only positions 1 through 3 by doubling, expecting \([-99,2,4,6,-99]\). Guards reveal writes beyond the intended subrange, but they do not prove absence of every possible invalid read; sanitizers add a different check.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

Exercises 1 and 2 are guided reconstructions of the worked examples; exercises
3-6 change an input, diagnose a defect, test a boundary and transfer the idea.
For each one, keep the calculation, output, diagram or failure policy you
produce so another reader can compare it with the worked cases. If the hint is
not enough, reread the mechanism paragraph and the bounded CPU assertion.

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

How many bytes hold 33 double values?

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A copy uses count where the API expects bytes. Which fixture catches it?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Define an empty-vector transfer policy.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design cleanup after a failed output allocation.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **equal numerical addresses imply interchangeable host and device pointers.**

For the concrete failure exercise, a copy uses count where the API expects bytes. Which fixture catches it?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-013_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-013: Explicit device allocation and transfer.
Read courses/cuda/cpp/guides/cuda-013.md and courses/cuda/cpp/lessons/cuda-013.md.
Direct prerequisites: `cuda-010`, `cuda-012`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-013_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-013_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
