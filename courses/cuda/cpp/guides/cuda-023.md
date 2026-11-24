# cuda-023: Stencils and boundary conditions

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-015`, `cuda-017`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement a stencil time step with a declared boundary condition and verify interior, boundary and conserved values.

Work through *Stencils and boundary conditions* with the concrete cases below. Finish with this evidence:
correct interior and boundary values plus a conserved or monotonic quantity appropriate to the chosen model. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

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

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-023_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-023_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel below is an excerpt from the chapter's complete [GPU reference](../references/cuda-023_gpu.cu). The full program adds device discovery, checked allocation and launch, completion checks and host validation. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

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

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [2.0, 4.0, 8.0]


def at(i):
    return values[i] if 0 <= i < len(values) else 0.0


out = [(at(i - 1) + at(i) + at(i + 1)) / 3 for i in range(len(values))]
assert out == [2.0, 14 / 3, 4.0]
assert values == [2.0, 4.0, 8.0]
print({"fixed_zero_mean": out, "original_preserved": values})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'fixed_zero_mean': [2.0, 4.666666666666667, 4.0], 'original_preserved': [2.0, 4.0, 8.0]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

An in-place left-to-right update reads newly computed values for later neighbors, creating a directional bias. Two-buffer updates read only the original row and swap roles after completion. For multiple GPU steps, preserve the dependency between launches or streams before swapping logical roles.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-023_gpu.cu) and separate
[GPU learner source](../lessons/cuda-023_gpu.cu) accompany this chapter.
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

Compute the periodic neighbor mean for \([2,4,8]\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

An image looks smooth but differs near the edge. Investigate what first?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What is a radius-one fixed-zero stencil of singleton \([6]\)?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the method to diffusion time stepping.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a visually plausible image proves the indexing and update ordering are correct.**

For the concrete failure exercise, an image looks smooth but differs near the edge. Investigate what first?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-023_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
