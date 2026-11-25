# cuda-005: Memory as addresses, ownership, shape and stride

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-004`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Calculate element and byte offsets for strided views and draw an explicit ownership and lifetime diagram.

**Scope:** Bytes versus elements, dtype, alignment, contiguous storage, row-major and column-major layout, strides, views, aliasing and ownership.

**Evidence to produce:** A correct offset table and explicit ownership/lifetime diagram.

## Purpose, vocabulary and mental model

A shape says how many logical coordinates exist. A stride says how far to move in storage when a coordinate increases by one. A row-major two-dimensional float array with row stride s elements places coordinate (r,c) at element offset r*s+c, then multiplies by the element size to obtain a byte offset. Padded rows use s greater than their logical width. A view can change shape and strides while borrowing the same allocation. Copying an address does not extend the allocation's lifetime or create independent data. Device and host pointers also carry an accessibility contract beyond their printed numeric value.

### Key terms

- **Stride:** The number of elements to move in storage when one logical coordinate increases by one.
- **Row-major layout:** A storage order in which elements of one row are contiguous, placing (r, c) at element offset r*s+c.
- **View:** An object that reinterprets shape and strides over storage it borrows without owning or copying it.
- **Aliasing:** Two names or pointers that refer to overlapping storage, so a write through one changes values seen through the other.
- **Pitch:** The padded row length in bytes chosen for an allocation, which can exceed the logical row width.

## Mathematical contract

\[
\operatorname{byteOffset}(r,c)=(r s+c)b
\]

Here r is row, c is column, s is row stride in elements, and b is bytes per element. All indices must satisfy logical bounds.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-005_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-005_cpu.py
```

## Worked example 1: trace the mechanism

Take a 2-by-3 float32 matrix with five stored elements per row. Coordinate (1,2) has element offset \(1\times 5+2=7\) and byte offset 28. The logical six values occupy a padded allocation of ten floats, or 40 bytes. Multiplying by logical width would read element 5 instead, a different location.

**Why:** Rows advance by the allocation's stride of 5, not the logical width 3, so padding is skipped correctly.

```python
rows, cols, stride, itemsize = 2, 3, 5, 4
assert ((1 * stride + 2) * itemsize) == 28
storage = [1, 2, 3, 4, 5, 6]
transposed = [[storage[r + c * 3] for c in range(2)] for r in range(3)]
assert transposed == [[1, 4], [2, 5], [3, 6]]
print({"offset_bytes": 28, "transpose_view_values": transposed})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'offset_bytes': 28, 'transpose_view_values': [[1, 4], [2, 5], [3, 6]]}
```

**Check:** The reference asserts (1 * 5 + 2) * 4 == 28 and prints offset_bytes 28.

## Worked example 2: change a meaningful condition

For contiguous \([[1,2,3],[4,5,6]]\), the row-major strides are (3,1) elements. A transposed view has shape (3,2) and strides (1,3). Coordinate (2,1) still refers to underlying element 5, value 6. There was no mandatory movement of bytes, and writing through the view can change the original owner.

**Why:** The view reuses the same six stored values, so offset 5 still holds value 6 with no copy.

**Check:** The reference rebuilds the view with storage[r + c * 3] and asserts [[1, 4], [2, 5], [3, 6]].

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Compute element offset as row times stored stride plus column, 1 * 5 + 2 = 7, then multiply by 4 bytes.

**Trap to avoid:** Using the logical width gives 1 * 3 + 2 = 5, reading a padding slot or the wrong row's element.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Swap the shape to (3, 2) and the strides to (1, 3), then evaluate coordinate (2, 1) as 2 * 1 + 1 * 3.

**Trap to avoid:** Copying data into a new transposed buffer before every read wastes bandwidth and detaches writes from the owner.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute the byte offset of (2,3) in a padded float64 matrix with row stride 8.

**Trap to avoid:** Using 4 bytes per element, a float32 habit, yields 76 bytes and lands mid-way through a different value.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A kernel receives only shape (3,2) for a transposed view and assumes contiguous rows. Diagnose the failure.

**Trap to avoid:** Assuming row-major from the shape reads element (0, 1) at offset 1, which holds value 2 instead of 4.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What changes for a one-column matrix with padding?

**Trap to avoid:** Treating the column as a dense vector and reading offsets 0, 1, 2 mixes values and padding.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Compare particle position reads in array-of-structures and structure-of-arrays.

**Trap to avoid:** Switching layout for this kernel alone ignores other consumers that read whole particles and the conversion cost.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Two arrays with the same shape necessarily have the same layout or independent storage.** Shape lists logical extents only; strides and ownership decide where elements live. Worked example 2 builds a transposed view with the same six values but strides (1,3), and writes through it change the original. Two arrays with identical shapes can therefore differ in layout and can even share storage.

## Self-check, retrieval and transfer

1. Give the element offset of (1,1) in a 2-by-3 float32 matrix with row stride 4.
2. Why must a kernel receive strides, not only a shape, for a view?
3. What risk does aliasing add when one buffer is both input and output?

Short answers are in the [separate explanations](../solutions/cuda-005_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
