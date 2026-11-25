# cuda-013: Explicit device allocation and transfer

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-010`, `cuda-012`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement checked device allocation and transfers that preserve guard values and clean up after an injected failure.

**Scope:** Allocation sizes, error checking, host/device memory spaces, transfer directions, buffer lifetimes and zero-length behavior.

**Evidence to produce:** Unchanged guard values, correct output, checked statuses and cleanup after an injected host-side failure.

## Purpose, vocabulary and mental model

cudaMalloc requests a number of bytes and returns a device allocation handle through a pointer argument. For n float elements, calculate n*sizeof(float), checking multiplication bounds for externally supplied sizes. cudaMemcpy also takes bytes and an explicit direction in the simple runtime API. The input owner must remain alive until the transfer finishes, and the device output must remain allocated until its final consumer completes. Host-to-device transfer supplies input; device-to-host transfer produces an observable result. A pointer is not a container with a length field, so the surrounding program must preserve size and lifetime metadata.

### Key terms

- **cudaMalloc:** The runtime call that reserves a number of bytes in device global memory and returns a device pointer.
- **cudaMemcpy:** A runtime copy between host and device memory that takes a byte count and an explicit direction.
- **Device pointer:** An address that is valid for device access and that ordinary host code must not dereference.
- **Guard value:** A known sentinel placed beyond the valid range so that an out-of-bounds write becomes detectable.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-013_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-013_cpu.py
```

## Worked example 1: trace the mechanism

Copy \([2,4,6,8]\) as float32. Four elements require 16 bytes. A request for four bytes copies only one float. Zero-initialized test data can hide that error, so use distinct nonzero entries and validate the entire result after the round trip.

**Why:** Copy APIs take bytes, so the size must be element count times element size.

```python
storage = [-99, 1, 2, 3, -99]
for i in range(1, 4):
    storage[i] *= 2
assert storage == [-99, 2, 4, 6, -99]
assert 4 * 4 == 16
print({"guarded_output": storage, "four_float32_bytes": 16})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'guarded_output': [-99, 2, 4, 6, -99], 'four_float32_bytes': 16}
```

**Check:** The reference asserts 4 * 4 == 16; compare all of [2, 4, 6, 8] after the round trip.

## Worked example 2: change a meaningful condition

Place sentinel values around a three-element target: \([-99,1,2,3,-99]\). Transform only positions 1 through 3 by doubling, expecting \([-99,2,4,6,-99]\). Guards reveal writes beyond the intended subrange, but they do not prove absence of every possible invalid read; sanitizers add a different check.

**Why:** Unchanged sentinels show that no write escaped the intended subrange.

**Check:** The reference asserts storage == [-99, 2, 4, 6, -99]; run a sanitizer for read checks.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Multiply four float32 elements by sizeof(float), giving 16 bytes, and copy that many.

**Trap to avoid:** Passing 4 as the byte count copies one float and leaves three elements uninitialized.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Surround the three targets with -99 sentinels and double only indices 1 to 3.

**Trap to avoid:** Assuming sentinels prove no invalid reads ignores that reads leave no trace in memory.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

How many bytes hold 33 double values?

**Trap to avoid:** Using 33 * 4 copies only half the doubles, as if they were floats.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A copy uses count where the API expects bytes. Which fixture catches it?

**Trap to avoid:** Using zero-filled buffers can hide a short copy because destination memory may also be zero.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Define an empty-vector transfer policy.

**Trap to avoid:** Calling the copy with a null source and zero bytes still relies on unclear API behavior.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design cleanup after a failed output allocation.

**Trap to avoid:** Continuing to copy results from an output pointer that was never allocated reads invalid memory.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Equal numerical addresses imply interchangeable host and device pointers.** Host and device pointers live in different address spaces, so a matching numerical value means nothing. Pass device pointers only to kernels and device APIs, move data with an explicit `cudaMemcpy` direction, and validate the full round trip as worked example 1 does with distinct nonzero values. Four float32 values need 16 bytes, so a request for 4 bytes copies only the first element.

## Self-check, retrieval and transfer

1. Why does worked example 1 use distinct nonzero values?
2. What do the sentinel values in worked example 2 detect?
3. When may the host input buffer be freed after a copy to the device?

Short answers are in the [separate explanations](../solutions/cuda-013_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
