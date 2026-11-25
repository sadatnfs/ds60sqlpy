# cuda-015: Two-dimensional indexing and image kernels

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`, `cuda-014`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Compute correct results on non-square images while preserving padding and stating the edge policy.

**Scope:** `dim3`, row/column mapping, leading dimensions, rectangular shapes, pitches and boundary policy.

**Evidence to produce:** Correct non-square results, preserved padding and explicit edge behavior.

## Purpose, vocabulary and mental model

A dim3 value holds three dimensions, though an image often uses only x and y. Map x to a column and y to a row, then calculate storage using the row stride. Logical width and stored leading dimension are different quantities. The grid must cover both axes, and each thread predicates both coordinate bounds before accessing storage. This is especially important for rectangular images because square examples can conceal a swapped width and height. If an allocation uses a byte pitch, convert coordinates using that byte quantity deliberately rather than treating it as an element stride.

### Key terms

- **dim3:** A CUDA type holding x, y and z extents for grid and block shapes.
- **Leading dimension:** The stored distance in elements between the starts of consecutive rows, which can exceed the logical width.
- **Pitched allocation:** A two-dimensional allocation whose row length in bytes, the pitch, is padded for alignment.
- **Boundary policy:** The declared rule for outputs whose coordinates or neighbors fall outside the image.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-015_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-015_cpu.py
```

## CUDA C++ kernel listing

An excerpt from the chapter's complete [GPU reference](../references/cuda-015_gpu.cu); the reading pad does not compile it.

```cpp
__global__ void brighten(int *image, std::size_t width, std::size_t height,
                         std::size_t stride) {
  const std::size_t col =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  const std::size_t row =
      static_cast<std::size_t>(blockIdx.y) * blockDim.y + threadIdx.y;
  if (row < height && col < width)
    image[row * stride + col] += 10;
}
```

## Worked example 1: trace the mechanism

Take a width-3, height-2 image stored as \([1,2,3,99,4,5,6,99]\) with stride four. Add ten to each real pixel. The expected storage is \([11,12,13,99,14,15,16,99]\). Both padding sentinels stay 99. Coordinate (1,2) means row one, column two, stored at index six.

**Why:** Stride four skips the padding slot in each row, so indices 3 and 7 are never touched.

```python
width, height, stride = 3, 2, 4
image = [1, 2, 3, 99, 4, 5, 6, 99]
for row in range(height):
    for col in range(width):
        image[row * stride + col] += 10
assert image == [11, 12, 13, 99, 14, 15, 16, 99]
print(image)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
[11, 12, 13, 99, 14, 15, 16, 99]
```

**Check:** The reference asserts the image equals [11, 12, 13, 99, 14, 15, 16, 99].

## Worked example 2: change a meaningful condition

A 4-by-2 thread block covers a 3-by-2 image with two unused x positions, one in each row. If the image becomes 2-by-3, grid height must also grow. Checking only the flattened offset can accidentally accept a logically invalid column that lands in the next row.

**Why:** Per-axis checks reject column 3 even though offset 3 lies inside the padded allocation.

**Check:** Swap the image to 2-by-3 and confirm grid height increases and every pixel is covered.

## Optional CUDA C++ laboratory

- [GPU learner source](../lessons/cuda-015_gpu.cu)
- [GPU reference](../references/cuda-015_gpu.cu)

Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. For each row and column add ten at row * 4 + col, leaving column 3 alone.

**Trap to avoid:** Looping over all eight storage slots adds ten to the 99 sentinels too.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Predicate x < width and y < height separately before forming any flat offset.

**Trap to avoid:** Checking only offset < stride * height accepts x = 3, which writes the padding slot.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Find grid dimensions for width 17, height 9 and blocks 8-by-4.

**Trap to avoid:** Using floor division gives 2 by 2 and misses column 16 and row 8.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can flattening before coordinate checks corrupt padding?

**Trap to avoid:** Relying on the allocation size as the bound treats padding as valid pixels.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Specify behavior for width zero.

**Trap to avoid:** Launching ceil(0 / 8) = 0 blocks in x yields an invalid configuration error.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Adapt the transform to RGB interleaved pixels.

**Trap to avoid:** Treating stride as pixels when it counts elements misplaces every row after the first.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Swapping grid axes only changes performance rather than which elements are touched.** Axis choice decides which coordinate each thread computes, so swapping x and y on a rectangular image touches different pixels. Worked example 2 shows a 3-by-2 image becoming 2-by-3: unless grid height grows and both coordinates are checked, some rows are skipped or padding is overwritten.

## Self-check, retrieval and transfer

1. For a width-3 image with stride 4, where is pixel (row 1, column 0) stored?
2. Why must a kernel check row and column separately rather than the flattened offset?
3. What should happen to padding sentinels after the transform?

Short answers are in the [separate explanations](../solutions/cuda-015_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-015: Two-dimensional indexing and image kernels.
Read courses/cuda/cpp/guides/cuda-015.md and courses/cuda/cpp/lessons/cuda-015.md.
Direct prerequisites: `cuda-005`, `cuda-014`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-015_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-015_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
