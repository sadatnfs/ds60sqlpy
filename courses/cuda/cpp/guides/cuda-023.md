# cuda-023: Stencils and boundary conditions

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-015`, `cuda-017`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a stencil time step with a declared boundary condition and verify interior, boundary and conserved values.

**Scope:** Neighborhood reuse, halo cells, read/write separation, time steps and physical versus computational boundaries.

**Evidence to produce:** Correct interior and boundary values plus a conserved or monotonic quantity appropriate to the chosen model.

## Purpose, vocabulary and mental model

A stencil computes each output from a neighborhood of input values. The boundary policy is part of the mathematics: clamped, periodic and fixed-zero boundaries describe different problems. Use separate input and output buffers for a time step so one update cannot change a neighbor's inputs halfway through the step. A tiled implementation loads a halo around its interior region because edge outputs need values from neighboring tiles. A barrier only protects data loaded by the same cooperating group; it does not legalize global in-place updates across independently scheduled blocks.

### Key terms

- **Stencil:** A computation in which each output depends on a fixed neighborhood of input values.
- **Halo:** The extra border of neighbor values that a tile loads so its edge outputs can be computed.
- **Ping-pong buffers:** Separate input and output arrays for each time step, swapped afterward, so updates never read partially updated neighbors.
- **Periodic boundary:** A boundary condition in which indices wrap around so the last element neighbors the first.

## Mathematical contract

\[
y_i=\frac{x_{i-1}+x_i+x_{i+1}}{3}
\]

The formula requires a separately stated boundary policy for indices outside the input. Input and output are distinct during one time step.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-023_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-023_cpu.py
```

## CUDA C++ kernel listing

An excerpt from the chapter's complete [GPU reference](../references/cuda-023_gpu.cu); the reading pad does not compile it.

```cpp
__global__ void neighbor_sum(const int *input, int *output, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    output[i] =
        (i > 0 ? input[i - 1] : 0) + input[i] + (i + 1 < n ? input[i + 1] : 0);
}
```

## Worked example 1: trace the mechanism

For \([2,4,8]\) with a three-point mean and fixed-zero outside values, one step gives \([2,\frac{14}{3},4]\). With clamped boundaries it gives \([\frac{8}{3},\frac{14}{3},\frac{20}{3}]\). Both are valid calculations, but they answer different questions. A reference must match the chosen policy.

**Why:** Index 0 sees 0 + 2 + 4 = 6 for mean 2, index 2 sees 4 + 8 + 0 for mean 4, and the middle sees 14 / 3.

```python
values = [2.0, 4.0, 8.0]


def at(i):
    return values[i] if 0 <= i < len(values) else 0.0


out = [(at(i - 1) + at(i) + at(i + 1)) / 3 for i in range(len(values))]
assert out == [2.0, 14 / 3, 4.0]
assert values == [2.0, 4.0, 8.0]
print({"fixed_zero_mean": out, "original_preserved": values})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'fixed_zero_mean': [2.0, 4.666666666666667, 4.0], 'original_preserved': [2.0, 4.0, 8.0]}
```

**Check:** The reference asserts out == [2.0, 14 / 3, 4.0] and that the input is still [2.0, 4.0, 8.0] afterward.

## Worked example 2: change a meaningful condition

An in-place left-to-right update reads newly computed values for later neighbors, creating a directional bias. Two-buffer updates read only the original row and swap roles after completion. For multiple GPU steps, preserve the dependency between launches or streams before swapping logical roles.

**Why:** Each output then depends only on the previous state, which matches the mathematical update for every index at once.

**Check:** Run one step both ways on [2, 4, 8] and confirm only the two-buffer version matches the reference values.

## Optional CUDA C++ laboratory

- [GPU learner source](../lessons/cuda-023_gpu.cu)
- [GPU reference](../references/cuda-023_gpu.cu)

Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Average each point with its two neighbors, substituting zero for indices -1 and 3 in [2, 4, 8].

**Trap to avoid:** Clamping silently while the spec says fixed-zero gives [8/3, 14/3, 20/3], a correct answer to a different question.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Read from the original buffer and write to a second one, swapping roles between steps or launches.

**Trap to avoid:** Updating in place left to right means index 1 reads the already smoothed index 0, which biases the result toward one direction.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute the periodic neighbor mean for \([2,4,8]\).

**Trap to avoid:** Applying the fixed-zero rule while calling it periodic gives 2 and 4 at the ends instead.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

An image looks smooth but differs near the edge. Investigate what first?

**Trap to avoid:** Loosening the tolerance until the test passes hides a halo or padding bug that will grow with image size.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What is a radius-one fixed-zero stencil of singleton \([6]\)?

**Trap to avoid:** Returning 6 because the array has no neighbors silently switches to the clamped rule.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the method to diffusion time stepping.

**Trap to avoid:** Running many steps in place in one kernel without a grid-wide dependency lets blocks read neighbors from the wrong step.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A visually plausible image proves the indexing and update ordering are correct.** Smooth-looking output can hide wrong boundaries or in-place updates that read already-updated neighbors. Worked example 1 shows two valid boundary policies giving different numbers, and worked example 2 shows in-place updates adding bias. Compare exact values against a reference with the chosen policy instead.

## Self-check, retrieval and transfer

1. What is the clamped three-point mean of the last element of [2,4,8]?
2. Why use two buffers per time step?
3. What is a halo in a tiled stencil?

Short answers are in the [separate explanations](../solutions/cuda-023_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-023: Stencils and boundary conditions.
Read courses/cuda/cpp/guides/cuda-023.md and courses/cuda/cpp/lessons/cuda-023.md.
Direct prerequisites: `cuda-015`, `cuda-017`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-023_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-023_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
