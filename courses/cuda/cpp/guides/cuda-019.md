# cuda-019: Tiled matrix multiplication and reuse

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-018`, `cuda-017`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Tiled matrix multiplication and reuse* with the concrete cases below. Finish with this evidence:
correctness plus a measured, scoped comparison with a reasoned interpretation even if the tile loses on a small input. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Tiling loads small regions of A and B into shared memory and reuses each value across several output calculations. For each k-phase, threads cooperatively load both tiles, synchronize, accumulate from the tiles, then synchronize again before overwriting shared storage for the next phase. Partial tiles require zero-filled invalid positions. An early return by tail threads can break the barrier contract. Tile size trades global reuse against shared storage, registers, occupancy and unused tail work. A tiled learning kernel is a correctness and reuse experiment, not an automatic replacement for a mature GEMM library.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-019_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-019_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The tiled kernel follows the phase structure above: cooperative loads with zero fill, a barrier before the tiles are read, and a second barrier before the next phase overwrites them. Out-of-range threads keep running so that they reach both barriers. Two 16-by-16 float tiles use 2 x 16 x 16 x 4 = 2048 bytes of shared memory per block. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

```cpp
constexpr int TILE = 16;

__global__ void tiled_matmul(const float *A, const float *B, float *C, int M,
                             int N, int K) {
  __shared__ float As[TILE][TILE];
  __shared__ float Bs[TILE][TILE];
  const int row = blockIdx.y * TILE + threadIdx.y;
  const int col = blockIdx.x * TILE + threadIdx.x;
  float sum = 0.0f;
  for (int phase = 0; phase < (K + TILE - 1) / TILE; ++phase) {
    const int a_col = phase * TILE + threadIdx.x;
    const int b_row = phase * TILE + threadIdx.y;
    As[threadIdx.y][threadIdx.x] =
        (row < M && a_col < K) ? A[row * K + a_col] : 0.0f;
    Bs[threadIdx.y][threadIdx.x] =
        (b_row < K && col < N) ? B[b_row * N + col] : 0.0f;
    __syncthreads(); // both tiles are complete before any thread reads them
    for (int k = 0; k < TILE; ++k)
      sum += As[threadIdx.y][k] * Bs[k][threadIdx.x];
    __syncthreads(); // all reads finish before the next phase overwrites tiles
  }
  if (row < M && col < N)
    C[row * N + col] = sum; // predicate the store; never return early
}
// Launch: dim3 block(TILE, TILE);
//         dim3 grid((N + TILE - 1) / TILE, (M + TILE - 1) / TILE);
```

## Worked example 1: trace the mechanism

For a 2-by-2 output tile and \(\mathrm{k}=2\), the four outputs need eight products. Loading four A values and four B values allows reuse across outputs. The naive per-output scheme conceptually reads sixteen scalar operands; the tile loads eight. Cache behavior can change actual transactions.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
k, tile = 5, 2
phases = [(start, min(start + tile, k)) for start in range(0, k, tile)]
assert phases == [(0, 2), (2, 4), (4, 5)]
assert 2 * 16 * 16 * 4 == 2048
print({"phases": phases, "two_tiles_bytes": 2048})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'phases': [(0, 2), (2, 4), (4, 5)], 'two_tiles_bytes': 2048}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

With \(\mathrm{k}=3\) and tile width two, the second phase contains one valid inner coordinate and one zero coordinate. Neutralizing invalid A and B entries preserves the sum. Synchronize after accumulation before the next cooperative load; otherwise a fast producer can overwrite data a slower thread still reads.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

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

Count phases for \(\mathrm{k}=5\) and tile width two.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is returning early for an out-of-range output thread dangerous?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How much shared storage do two 16-by-16 float tiles use?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

A tiled kernel loses on a tiny matrix. Is that a bug?

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **shared memory automatically makes a kernel faster.**

For the concrete failure exercise, why is returning early for an out-of-range output thread dangerous?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-019_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-019: Tiled matrix multiplication and reuse.
Read courses/cuda/cpp/guides/cuda-019.md and courses/cuda/cpp/lessons/cuda-019.md.
Direct prerequisites: `cuda-018`, `cuda-017`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-019_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-019_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
