# cuda-066: Shape, dtype, stride and layout are a contract

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-065`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Calculate offset (1,1).
- Change dtype to float64.
- Describe a transposed view.
- Find the contiguous-only bug.
- Specify negative-stride support.
- Design layout contract tests.

## Mechanism and vocabulary

Shape describes logical coordinates; strides describe the byte displacement when one coordinate increases by one. A contiguous row-major matrix with three float32 columns has strides (12, 4). A slice selecting alternate columns changes the last stride without necessarily copying storage. Its shape alone cannot tell a raw kernel how to find the next element.

An address is the allocation base plus view offset plus the sum of index times stride. Dtype determines interpretation and element width, not just a display label. A kernel accepting only contiguous float32 data should validate those conditions or explicitly pack a copy and account for it. Supporting arbitrary strides requires a different indexing contract. Never reinterpret float64 bytes as float32 because the element count happens to match.



### Key terms

- **Shape:** The number of elements along each axis of an array.
- **Stride:** The number of bytes to step in memory to move one position along an axis.
- **Contiguous row-major layout:** A layout where the last axis varies fastest and the elements occupy one gap-free block of memory.
- **Transposed view:** An array that reuses the same buffer with swapped shape and strides instead of copying data.
- **Negative stride:** A stride that walks backward through the buffer, as produced by a reversed slice.

## Worked examples

### Worked example 1

For a 2 by 3 float32 array, coordinate (1, 2) is \(1\times12+2\times4=20\) bytes from the base. The allocation occupies 24 bytes.

### Worked example 2

A column slice choosing columns 0 and 2 has shape (2, 2), strides (12, 8) and a 16-byte logical payload. Its covered storage spans 24 bytes; logical bytes and storage span differ.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-066_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-066_cpu.py
```

```python
def offset(indices, strides):
    return sum(i * s for i, s in zip(indices, strides, strict=True))


assert offset((1, 2), (12, 4)) == 20
assert offset((1, 1), (12, 8)) == 20
assert offset((2, 1), (4, 12)) == 20
print("CPU layout model:", offset((1, 2), (12, 4)), "bytes")
```

**Expected observation:** All three views address byte offset 20.

## Optional NVIDIA CUDA lab

**CuPy on NVIDIA CUDA** needs the `cuda-python` profile; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.arange(6, dtype=cp.float32).reshape(2, 3)
view = x[:, ::2]
assert view.shape == (2, 2)
assert view.strides == (12, 8)
cp.testing.assert_array_equal(view, cp.asarray([[0, 2], [3, 5]], dtype=cp.float32))
cp.cuda.get_current_stream().synchronize()
print("CUDA layout:", view.shape, view.strides, cp.asnumpy(view).tolist())
```

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-066.md) before opening hints.

### Exercise 1: Calculate offset (1,1)

**Trap to avoid:** Computing `1*3 + 1` and calling the answer 4 gives an element index, not a byte offset. Using the sliced view strides `(12, 8)` gives 20, which is the address of a different element in the original storage.

### Exercise 2: Change dtype to float64

**Trap to avoid:** Keeping strides `(12, 4)` and only relabeling the dtype reads half of each float64 as a float32. The element count matches, which is why the bug is easy to miss, but every value is garbage.

### Exercise 3: Describe a transposed view

**Trap to avoid:** Assuming the transpose is contiguous and indexing it with `row*2 + col` reads the original storage in the wrong order. A raw kernel given only the data pointer and new shape silently computes on the untransposed matrix.

### Exercise 4: Find the contiguous-only bug

**Trap to avoid:** Fixing it by calling a reshape on the slice can hide the bug: reshape may copy, so the kernel becomes correct but writes go to a temporary and the original view never changes.

### Exercise 5: Specify negative-stride support

**Trap to avoid:** Taking absolute values of strides makes indices non-negative and appears to work, but it reads the columns in the original order, so a reversed view returns unreversed data.

### Exercise 6: Design layout contract tests

**Trap to avoid:** Testing only random contiguous arrays of various sizes gives high coverage numbers but never exercises a non-unit stride, which is the exact contract this chapter is about.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Count how many float32 values precede (1,1) in row-major storage, then convert elements to bytes.
2. Keep the shape `(2, 3)` fixed and recompute both strides with an 8-byte itemsize before touching any offset.
3. Swap the axes and ask how far in bytes one step along each new axis moves through the original storage.
4. Apply `row*width+col` to the column slice of worked example 2 and list which original columns it reads.
5. Write the address formula with a negative last stride and check which integer type the index arithmetic must use.
6. Pick one case per assumption: contiguity, the stride formula, launch bounds and dtype. Name what each case would catch.

## Common mistakes and self-check

A frequent mistake is passing a sliced or transposed array to a kernel that assumes contiguous row-major data, so it computes `row*width+col` and silently reads the wrong elements. Worked example 2 shows the trap: the column slice has strides `(12, 8)`, not `(8, 4)`. Fix it by checking strides and dtype at the kernel boundary, then either rejecting the view, packing an explicit contiguous copy whose cost you report, or indexing with the real strides.

**Evidence limit:** The reference checks byte offsets for three views of one 2 by 3 float32 matrix. Offset arithmetic is exact here, but it does not test device alignment rules, memory coalescing or how a particular library decides to copy a non-contiguous view.

1. What does a stride tell you that a shape does not?
2. Why do logical bytes and storage span differ for the column slice?
3. Why is reinterpreting float64 bytes as float32 wrong even when element counts match?

Answers: [self-check answers](../solutions/cuda-066_solutions.md#self-check-answers).

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-066: Shape, dtype, stride and layout are a contract.
Read courses/cuda/python/guides/cuda-066.md and courses/cuda/python/lessons/cuda-066.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
