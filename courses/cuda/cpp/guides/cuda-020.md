# cuda-020: Parallel reductions and the order of arithmetic

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-006`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement a two-stage block reduction with correct tails and a justified floating-point tolerance.

Work through *Parallel reductions and the order of arithmetic* with the concrete cases below. Finish with this evidence:
correct tails and a justified tolerance, with no assumption of a fixed block completion order. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

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

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-020_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-020_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel below is an excerpt from the chapter's complete [GPU reference](../references/cuda-020_gpu.cu). The full program adds device discovery, checked allocation and launch, completion checks and host validation. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

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

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

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

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
[[6, 2, 3, 4], [9, 6], [15]]
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For \([10^{16},1,-10^{16}]\), different valid sum trees can disagree. Compare against a compensated or higher-precision reference and report error. Do not require a GPU result to copy an arbitrary CPU association, and do not enlarge tolerance enough to hide dropped tail elements.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-020_gpu.cu) and separate
[GPU learner source](../lessons/cuda-020_gpu.cu) accompany this chapter.
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

Choose an identity for maximum over \([-7,-3,-9]\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

One block waits for a counter from all other blocks. Explain the deadlock risk.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Define sum for zero and one element.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer reduction to mean.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **floating-point addition is associative or one block can safely wait for every other block in an ordinary launch.**

For the concrete failure exercise, one block waits for a counter from all other blocks. Explain the deadlock risk.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-020_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
