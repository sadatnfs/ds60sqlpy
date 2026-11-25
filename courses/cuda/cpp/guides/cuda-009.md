# cuda-009: C++ essentials specifically needed at the GPU boundary

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Write CPU reference tests for a pointer-and-size interface and explain the lifetime of each buffer.

**Scope:** Fixed-width types, references and pointers, `const`, contiguous containers, `size_t`, conversions, function parameters and compile-time versus runtime values.

**Evidence to produce:** CPU reference tests and a lifetime explanation.

## Purpose, vocabulary and mental model

A pointer identifies storage; a size defines the range your function may use. Pair them explicitly. A const input pointer prevents writes through that pointer, but it does not establish unique ownership or guarantee that another alias cannot modify storage. A vector owns contiguous elements and can lend its data pointer while it remains alive and does not reallocate. A device function cannot generally use an ordinary host vector object because its implementation, allocator and storage belong to the host environment. Use plain element buffers and explicit shape metadata at the boundary, with deliberate integer-width choices for address arithmetic.

### Key terms

- **RAII:** Resource Acquisition Is Initialization, a C++ idiom that ties releasing a resource to an owning object's destructor.
- **Const pointer parameter:** A parameter such as `const float*` that forbids writes through that pointer but does not stop other aliases from writing.
- **size_t:** An unsigned integer type wide enough to hold the size of any object, used for element counts and byte sizes.
- **Dangling pointer:** A pointer that still holds an address after its storage was freed or reallocated, so dereferencing it is undefined behavior.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-009_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-009_cpu.py
```

## Worked example 1: trace the mechanism

A CPU affine transform accepts input, output, count, scale and bias. For input \([-1,0,2]\), scale 3 and bias 1, the result is \([-2,1,7]\). Reject mismatched ranges before indexing. If input and output overlap, either document in-place safety or reject that case; const alone does not answer it.

**Why:** Each output depends only on its own input, so the map is correct for any order of evaluation.

```python
values = [-1, 0, 2]
result = [3 * value + 1 for value in values]
assert result == [-2, 1, 7]
padded = [1, 2, 99, 3, 4, 99]
row_sums = [sum(padded[r * 3 : r * 3 + 2]) for r in range(2)]
assert row_sums == [3, 7]
print({"affine": result, "row_sums": row_sums})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'affine': [-2, 1, 7], 'row_sums': [3, 7]}
```

**Check:** The reference asserts the result equals [-2, 1, 7]; add an aliased call and state its documented policy.

## Worked example 2: change a meaningful condition

A function returning `vector<float>{1,2,3}.data()` returns a pointer to storage whose owner is destroyed at the end of the expression. The pointer value may still print, but dereferencing it is invalid. Return the owning vector, or pass caller-owned storage into the function. Keeping a numeric address does not keep an allocation alive.

**Why:** The temporary vector is destroyed at the end of the full expression, so its storage is released.

**Check:** Build with address sanitizer on the host; the dangling read is reported as use after free.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Validate that input and output lengths match the count, then compute 3 * x + 1 for each of [-1, 0, 2].

**Trap to avoid:** Assuming const on the input makes in-place calls safe ignores aliasing when output points to the same storage.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Return the owning vector by value or accept caller storage, never a pointer into a temporary.

**Trap to avoid:** Printing the pointer to prove it is valid fails because a numeric address says nothing about lifetime.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Describe a row-sum function's minimum buffer metadata for padded storage.

**Trap to avoid:** Passing only rows and columns makes row 1 start at offset 2, reading the padding value 99.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A vector grows after its data pointer was saved. What must be checked?

**Trap to avoid:** Calling reserve once and then appending past that capacity still reallocates and invalidates the pointer.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How should count zero be handled?

**Trap to avoid:** Computing input + count - 1 as a last element pointer creates an invalid pointer before input.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Why should a host pointer not be reinterpreted as a device allocation?

**Trap to avoid:** Casting a host float pointer to a device pointer type and launching causes an illegal address fault.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Copying a pointer copies the data, or a host container can be passed to device code unchanged.** A pointer copy duplicates an address, not the storage, so both copies see the same bytes and the same lifetime. Worked example 2 returns a pointer whose vector is already destroyed. Host containers also live in host memory, so device code needs an explicit device allocation and transfer.

## Self-check, retrieval and transfer

1. What two values should travel together whenever a buffer crosses a function boundary?
2. What does `const float*` guarantee and what does it not?
3. Why is `size_t` preferred for element counts?

Short answers are in the [separate explanations](../solutions/cuda-009_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-009: C++ essentials specifically needed at the GPU boundary.
Read courses/cuda/cpp/guides/cuda-009.md and courses/cuda/cpp/lessons/cuda-009.md.
Direct prerequisites: `cuda-005`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-009_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-009_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
