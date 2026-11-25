# cuda-020: Parallel reductions and the order of arithmetic

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-006`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a two-stage block reduction with correct tails and a justified floating-point tolerance.

**Scope:** Tree reduction, partial sums, neutral elements, non-power-of-two lengths and numerical ordering.

**Evidence to produce:** Correct tails and a justified tolerance, with no assumption of a fixed block completion order.

## Purpose, vocabulary and mental model

A reduction combines values with an operation and identity. A tree reduces dependency depth compared with a serial chain, but it changes floating-point addition order. A block reduction usually first writes one partial per block; another launch combines those partials. This creates a real cross-block dependency without an unsafe grid-wide spin barrier. Tail threads contribute the identity, such as zero for addition. For a maximum, zero is not a neutral value if all inputs are negative. Define empty input explicitly and retain a higher-accuracy CPU oracle for floating-point work.

### Key terms

- **Identity element:** A value that leaves the result unchanged, such as zero for a sum or negative infinity for a maximum.
- **Tree reduction:** A reduction that combines pairs in rounds, cutting dependency depth to about log2(n).
- **Block partial sum:** The per-block value that a second stage combines into the final answer.
- **Associativity:** The property that grouping does not change a result, which real addition has but floating-point addition only approximates.

## Mathematical contract

\[
s=\sum_{i=0}^{n-1}x_i
\]

This specifies the mathematical sum. The chosen parallel association affects finite-precision rounding, so an error policy is still required.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-020_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-020_cpu.py
```

## CUDA C++ kernel listing

An excerpt from the chapter's complete [GPU reference](../references/cuda-020_gpu.cu); the reading pad does not compile it.

```cpp
__global__ void block_sums(const int *input, int *output, std::size_t n) {
  __shared__ int tile[64];
  const unsigned lane = threadIdx.x;
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + lane;
  tile[lane] = i < n ? input[i] : 0;
  __syncthreads();
  for (unsigned width = 32; width > 0; width /= 2) {
    if (lane < width)
      tile[lane] += tile[lane + width];
    __syncthreads();
  }
  if (lane == 0)
    output[blockIdx.x] = tile[0];
}
```

## Worked example 1: trace the mechanism

Pad \([1,2,3,4,5]\) to \([1,2,3,4,5,0,0,0]\). A halving tree produces pairwise states \([6,2,3,4]\), then \([9,6]\), then \([15]\). Each phase needs the appropriate communication ordering. Exact integer arithmetic makes ownership mistakes visible without rounding ambiguity.

**Why:** Zeros preserve the sum, and each phase halves the active values until one remains.

```python
values = [1, 2, 3, 4, 5, 0, 0, 0]
width = len(values) // 2
trace = []
while width:
    for i in range(width):
        values[i] += values[i + width]
    trace.append(values[:width])
    width //= 2
assert trace == [[6, 2, 3, 4], [9, 6], [15]]
print(trace)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
[[6, 2, 3, 4], [9, 6], [15]]
```

**Check:** The reference asserts trace == [[6, 2, 3, 4], [9, 6], [15]].

## Worked example 2: change a meaningful condition

For \([10^{16},1,-10^{16}]\), different valid sum trees can disagree. Compare against a compensated or higher-precision reference and report error. Do not require a GPU result to copy an arbitrary CPU association, and do not enlarge tolerance enough to hide dropped tail elements.

**Why:** Different trees round differently, and both can be valid floating sums.

**Check:** Compute math.fsum on the fixture and compare each tree's result to 1.0.

## Optional CUDA C++ laboratory

- [GPU learner source](../lessons/cuda-020_gpu.cu)
- [GPU reference](../references/cuda-020_gpu.cu)

Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Pad five values to eight with zeros, then add element i + width into i while width halves.

**Trap to avoid:** Padding with ones changes the total to 18 instead of 15.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Compare the result with a compensated or wider reference and report the error.

**Trap to avoid:** Requiring an exact match with sequential CPU order rejects a valid GPU tree.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Choose an identity for maximum over \([-7,-3,-9]\).

**Trap to avoid:** Starting from zero returns 0 for an all-negative input instead of -3.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

One block waits for a counter from all other blocks. Explain the deadlock risk.

**Trap to avoid:** Adding more waiting blocks makes the deadlock more likely, not less.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Define sum for zero and one element.

**Trap to avoid:** Launching a zero-block reduction for empty input triggers an invalid configuration.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer reduction to mean.

**Trap to avoid:** Dividing every partial sum by its block count averages unequal blocks wrongly.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Floating-point addition is associative or one block can safely wait for every other block in an ordinary launch.** Floating-point addition rounds at each step, so different trees give different answers, as worked example 2 shows. Blocks also have no guaranteed co-residency, so a block spinning on a counter can wait forever for a block that never starts. Combine block partials in a second launch.

## Self-check, retrieval and transfer

1. Trace the halving tree for [3,1,4,1].
2. What identity does a product reduction use for tail threads?
3. Why compare a float reduction against a compensated reference instead of a plain CPU loop?

Short answers are in the [separate explanations](../solutions/cuda-020_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-020: Parallel reductions and the order of arithmetic.
Read courses/cuda/cpp/guides/cuda-020.md and courses/cuda/cpp/lessons/cuda-020.md.
Direct prerequisites: `cuda-017`, `cuda-006`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-020_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-020_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
