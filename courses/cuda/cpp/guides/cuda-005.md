# cuda-005: Memory as addresses, ownership, shape and stride

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-004`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Memory as addresses, ownership, shape and stride* with the concrete cases below. Finish with this evidence:
a correct offset table and explicit ownership/lifetime diagram. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A shape says how many logical coordinates exist. A stride says how far to move in storage when a coordinate increases by one. A row-major two-dimensional float array with row stride s elements places coordinate (r,c) at element offset r*s+c, then multiplies by the element size to obtain a byte offset. Padded rows use s greater than their logical width. A view can change shape and strides while borrowing the same allocation. Copying an address does not extend the allocation's lifetime or create independent data. Device and host pointers also carry an accessibility contract beyond their printed numeric value.

## Mathematical contract

\[
\operatorname{byteOffset}(r,c)=(r s+c)b
\]

Here r is row, c is column, s is row stride in elements, and b is bytes per element. All indices must satisfy logical bounds.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-005_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-005_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Take a 2-by-3 float32 matrix with five stored elements per row. Coordinate (1,2) has element offset \(1\times 5+2=7\) and byte offset 28. The logical six values occupy a padded allocation of ten floats, or 40 bytes. Multiplying by logical width would read element 5 instead, a different location.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
rows, cols, stride, itemsize = 2, 3, 5, 4
assert ((1 * stride + 2) * itemsize) == 28
storage = [1, 2, 3, 4, 5, 6]
transposed = [[storage[r + c * 3] for c in range(2)] for r in range(3)]
assert transposed == [[1, 4], [2, 5], [3, 6]]
print({"offset_bytes": 28, "transpose_view_values": transposed})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'offset_bytes': 28, 'transpose_view_values': [[1, 4], [2, 5], [3, 6]]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For contiguous \([[1,2,3],[4,5,6]]\), the row-major strides are (3,1) elements. A transposed view has shape (3,2) and strides (1,3). Coordinate (2,1) still refers to underlying element 5, value 6. There was no mandatory movement of bytes, and writing through the view can change the original owner.

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

Compute the byte offset of (2,3) in a padded float64 matrix with row stride 8.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A kernel receives only shape (3,2) for a transposed view and assumes contiguous rows. Diagnose the failure.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What changes for a one-column matrix with padding?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Compare particle position reads in array-of-structures and structure-of-arrays.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **two arrays with the same shape necessarily have the same layout or independent storage.**

For the concrete failure exercise, a kernel receives only shape (3,2) for a transposed view and assumes contiguous rows. Diagnose the failure.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-005_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-005: Memory as addresses, ownership, shape and stride.
Read courses/cuda/cpp/guides/cuda-005.md and courses/cuda/cpp/lessons/cuda-005.md.
Direct prerequisites: `cuda-004`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-005_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-005_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
