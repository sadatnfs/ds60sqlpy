# cuda-014: One-dimensional indexing that survives awkward sizes

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-004`, `cuda-013`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Prove that a grid-stride loop writes every output element exactly once, including the tail.

Work through *One-dimensional indexing that survives awkward sizes* with the concrete cases below. Finish with this evidence:
every output element is written exactly once and tails match the CPU reference. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A one-dimensional launch gives a thread the starting index blockIdx.x*blockDim.x+threadIdx.x. A grid-stride loop advances that index by blockDim.x*gridDim.x until it reaches n. Every nonnegative index has one remainder modulo the positive stride, so exactly one starting thread owns it. Cast to a sufficiently wide integer before multiplying dimensions; widening after an overflow is too late. Ceiling division supplies enough threads for one-element mapping, but a grid-stride loop also allows a bounded grid to cover a much larger input. A bounds test is required even when most demonstration sizes divide evenly.

### Key terms

- **Global thread index:** The value `blockIdx.x * blockDim.x + threadIdx.x` that identifies one thread across the whole grid.
- **Ceiling division:** The calculation (n + b - 1) / b that gives enough blocks of size b to cover n elements.
- **Grid-stride loop:** A loop that advances each thread's index by the total number of threads in the grid until it reaches n.
- **Bounds predicate:** A condition such as `i < n` that keeps threads beyond the data from reading or writing memory.

## Mathematical contract

\[
i=t+kG,\qquad 0\leq t<G,\quad k\geq0
\]

G is the positive grid stride and t is a unique starting thread index. Each valid i has a unique quotient and remainder, establishing coverage without duplicate ownership.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-014_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-014_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel below is an excerpt from the chapter's complete [GPU reference](../references/cuda-014_gpu.cu). The full program adds device discovery, checked allocation and launch, completion checks and host validation. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

```cpp
__global__ void vector_add(const int *a, const int *b, int *out,
                           std::size_t n) {
  const std::size_t start =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  const std::size_t stride = static_cast<std::size_t>(gridDim.x) * blockDim.x;
  for (std::size_t i = start; i < n; i += stride)
    out[i] = a[i] + b[i];
}
```

## Worked example 1: trace the mechanism

Use two blocks of four threads for \(\mathrm{n}=19\). Thread 0 owns indices 0,8,16; thread 1 owns 1,9,17; thread 2 owns 2,10,18; thread 3 owns 3,11. Every element has exactly one owner. This ownership trace is CPU reasoning, not a simulator of warp scheduling or GPU timing.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
n, stride = 19, 8
owners = [list(range(t, n, stride)) for t in range(stride)]
flat = [i for group in owners for i in group]
assert sorted(flat) == list(range(n)) and len(set(flat)) == n
assert owners[0] == [0, 8, 16]
print({"thread_0": owners[0], "all_elements_written_once": True})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'thread_0': [0, 8, 16], 'all_elements_written_once': True}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For x=\([0,1,2,3,4]\) and y=\([5,4,3,2,1]\), vector addition returns five fives. Extend the fixture to \(\mathrm{n}=33\) with distinct values to expose a tail just beyond a warp boundary. Test empty, singleton and a larger odd prime as well.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-014_gpu.cu) and separate
[GPU learner source](../lessons/cuda-014_gpu.cu) accompany this chapter.
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

Give the indices owned by starting thread 5 when \(\mathrm{stride}=8\) and \(\mathrm{n}=22\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A kernel tests `i <= n` instead of `i < n`. Diagnose it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How many blocks are required for \(\mathrm{n}=33\) with 32 threads under one-element mapping?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the proof to a streaming chunk with a global offset.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **removing the bounds condition is harmless because a chosen demo length is divisible by the block size.**

For the concrete failure exercise, a kernel tests `i <= n` instead of `i < n`. Diagnose it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-014_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-014: One-dimensional indexing that survives awkward sizes.
Read courses/cuda/cpp/guides/cuda-014.md and courses/cuda/cpp/lessons/cuda-014.md.
Direct prerequisites: `cuda-004`, `cuda-013`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-014_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-014_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
