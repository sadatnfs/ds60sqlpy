# cuda-015: Two-dimensional indexing and image kernels

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`, `cuda-014`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Compute correct results on non-square images while preserving padding and stating the edge policy.

Work through *Two-dimensional indexing and image kernels* with the concrete cases below. Finish with this evidence:
correct non-square results, preserved padding and explicit edge behavior. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A dim3 value holds three dimensions, though an image often uses only x and y. Map x to a column and y to a row, then calculate storage using the row stride. Logical width and stored leading dimension are different quantities. The grid must cover both axes, and each thread predicates both coordinate bounds before accessing storage. This is especially important for rectangular images because square examples can conceal a swapped width and height. If an allocation uses a byte pitch, convert coordinates using that byte quantity deliberately rather than treating it as an element stride.

### Key terms

- **dim3:** A CUDA type holding x, y and z extents for grid and block shapes.
- **Leading dimension:** The stored distance in elements between the starts of consecutive rows, which can exceed the logical width.
- **Pitched allocation:** A two-dimensional allocation whose row length in bytes, the pitch, is padded for alignment.
- **Boundary policy:** The declared rule for outputs whose coordinates or neighbors fall outside the image.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-015_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-015_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel below is an excerpt from the chapter's complete [GPU reference](../references/cuda-015_gpu.cu). The full program adds device discovery, checked allocation and launch, completion checks and host validation. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

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

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
width, height, stride = 3, 2, 4
image = [1, 2, 3, 99, 4, 5, 6, 99]
for row in range(height):
    for col in range(width):
        image[row * stride + col] += 10
assert image == [11, 12, 13, 99, 14, 15, 16, 99]
print(image)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
[11, 12, 13, 99, 14, 15, 16, 99]
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A 4-by-2 thread block covers a 3-by-2 image with two unused x positions, one in each row. If the image becomes 2-by-3, grid height must also grow. Checking only the flattened offset can accidentally accept a logically invalid column that lands in the next row.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-015_gpu.cu) and separate
[GPU learner source](../lessons/cuda-015_gpu.cu) accompany this chapter.
They are standalone files with bounded fixtures, checked runtime calls and host
validation. The learner source intentionally reports incomplete implementation
until you add the chapter's algorithm and assertions. It must never return a
fake GPU success on a CPU machine. Follow the [manual GPU workflow](../README.md)
for exact compilation and execution paths. If the classroom offers the optional
CUDA C++ variant, its capability notice must confirm actual runtime readiness.

The reference contains an explicit no-device failure, launch and completion
checks, and returned-value validation. Source review and CPU reference checks do
not qualify this .cu file on your hardware. Preserve compilation, actual device
execution and sanitizer evidence separately. Exercise 4 is a reasoning diagnosis;
do not deliberately launch a hanging kernel or reset a shared GPU to reproduce it.

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

Find grid dimensions for width 17, height 9 and blocks 8-by-4.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can flattening before coordinate checks corrupt padding?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Specify behavior for width zero.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Adapt the transform to RGB interleaved pixels.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **swapping grid axes only changes performance rather than which elements are touched.**

For the concrete failure exercise, why can flattening before coordinate checks corrupt padding?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-015_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
