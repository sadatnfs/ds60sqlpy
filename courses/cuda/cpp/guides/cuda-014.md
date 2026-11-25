# cuda-014: One-dimensional indexing that survives awkward sizes

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-004`, `cuda-013`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Prove that a grid-stride loop writes every output element exactly once, including the tail.

**Scope:** Global thread index, ceiling division, bounds predicates and grid-stride loops.

**Evidence to produce:** Every output element is written exactly once and tails match the CPU reference.

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

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-014_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-014_cpu.py
```

## CUDA C++ kernel listing

An excerpt from the chapter's complete [GPU reference](../references/cuda-014_gpu.cu); the reading pad does not compile it.

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

**Why:** Indices congruent to t modulo 8 belong to thread t only, so the eight lists partition 0 to 18.

```python
n, stride = 19, 8
owners = [list(range(t, n, stride)) for t in range(stride)]
flat = [i for group in owners for i in group]
assert sorted(flat) == list(range(n)) and len(set(flat)) == n
assert owners[0] == [0, 8, 16]
print({"thread_0": owners[0], "all_elements_written_once": True})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'thread_0': [0, 8, 16], 'all_elements_written_once': True}
```

**Check:** The reference asserts the sorted union equals range(19) with 19 unique entries, and thread 0 owns [0, 8, 16].

## Worked example 2: change a meaningful condition

For x=\([0,1,2,3,4]\) and y=\([5,4,3,2,1]\), vector addition returns five fives. Extend the fixture to \(\mathrm{n}=33\) with distinct values to expose a tail just beyond a warp boundary. Test empty, singleton and a larger odd prime as well.

**Why:** Every pair sums to five, and 33 places one element past the first 32-lane warp.

**Check:** Compare all 33 outputs with a host loop and confirm index 32 holds its own distinct sum.

## Optional CUDA C++ laboratory

- [GPU learner source](../lessons/cuda-014_gpu.cu)
- [GPU reference](../references/cuda-014_gpu.cu)

Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Set stride to the total thread count 2 * 4 = 8 and list i, i + 8, i + 16 below 19 for each thread.

**Trap to avoid:** Using blockDim.x = 4 as the stride makes block 1 revisit indices block 0 already owns.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Add [0, 1, 2, 3, 4] and [5, 4, 3, 2, 1], then repeat with 33 distinct values and empty and singleton inputs.

**Trap to avoid:** Testing only with five elements never crosses a block or warp edge, so a dropped tail stays hidden.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Give the indices owned by starting thread 5 when \(\mathrm{stride}=8\) and \(\mathrm{n}=22\).

**Trap to avoid:** Stopping at i <= n would admit 22 if it appeared, one past the last element.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A kernel tests `i <= n` instead of `i < n`. Diagnose it.

**Trap to avoid:** Allocating n + 1 elements hides the write but leaves the logical contract broken.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How many blocks are required for \(\mathrm{n}=33\) with 32 threads under one-element mapping?

**Trap to avoid:** Using 33 / 32 with integer division gives one block and loses element 32.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the proof to a streaming chunk with a global offset.

**Trap to avoid:** Adding the offset first and checking only the global bound can overrun a shorter final chunk.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Removing the bounds condition is harmless because a chosen demo length is divisible by the block size.** A demo length is not the contract. Real inputs arrive at sizes such as 19 or 33, and worked example 1 shows the final pass of a grid-stride loop covering only part of the stride. Without `i < n` the extra threads read and write past the allocation, which may corrupt memory silently.

## Self-check, retrieval and transfer

1. In worked example 1, why does thread 3 own only two indices?
2. Why cast to a wide integer before multiplying block index by block size?
3. What does a grid-stride loop give you that a one-element mapping does not?

Short answers are in the [separate explanations](../solutions/cuda-014_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
