# cuda-019: Tiled matrix multiplication and reuse

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-018`, `cuda-017`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a tiled matrix multiplication and report a scoped timing comparison with a reasoned interpretation.

**Scope:** Tile loading, shared-memory reuse, synchronization between phases, tail predicates and resource costs.

**Evidence to produce:** Correctness plus a measured, scoped comparison with a reasoned interpretation even if the tile loses on a small input.

## Purpose, vocabulary and mental model

Tiling loads small regions of A and B into shared memory and reuses each value across several output calculations. For each k-phase, threads cooperatively load both tiles, synchronize, accumulate from the tiles, then synchronize again before overwriting shared storage for the next phase. Partial tiles require zero-filled invalid positions. An early return by tail threads can break the barrier contract. Tile size trades global reuse against shared storage, registers, occupancy and unused tail work. A tiled learning kernel is a correctness and reuse experiment, not an automatic replacement for a mature GEMM library.

### Key terms

- **Tile:** A small submatrix loaded into shared memory so each value is reused by several output calculations.
- **Data reuse:** The number of times one loaded value contributes to results before it is replaced.
- **Zero-fill:** Writing zeros into tile positions outside the matrix so partial tiles still produce correct sums.
- **Tile phase:** One step along the shared dimension in which threads load, synchronize, accumulate and synchronize again.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-019_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-019_cpu.py
```

## CUDA C++ kernel listing

The tiled kernel follows the phase structure above: cooperative loads with zero fill, a barrier before the tiles are read, and a second barrier before the next phase overwrites them. Out-of-range threads keep running so that they reach both barriers. Two 16-by-16 float tiles use 2 x 16 x 16 x 4 = 2048 bytes of shared memory per block.

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

**Why:** Each loaded value serves two outputs, halving reads from sixteen to eight.

```python
k, tile = 5, 2
phases = [(start, min(start + tile, k)) for start in range(0, k, tile)]
assert phases == [(0, 2), (2, 4), (4, 5)]
print({"phases": phases})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'phases': [(0, 2), (2, 4), (4, 5)]}
```

**Check:** Enumerate operands per output and confirm each loaded value appears twice.

## Worked example 2: change a meaningful condition

With \(\mathrm{k}=3\) and tile width two, the second phase contains one valid inner coordinate and one zero coordinate. Neutralizing invalid A and B entries preserves the sum. Synchronize after accumulation before the next cooperative load; otherwise a fast producer can overwrite data a slower thread still reads.

**Why:** Zero products leave the sum unchanged, and the second barrier protects the tile.

**Check:** Compute a 2-by-3 times 3-by-2 product with tiles and compare to the naive result.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Count loads per tile: two A values per row times two rows, and the same for B.

**Trap to avoid:** Assuming caches already provide that reuse makes the tile seem pointless without evidence.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Split k = 3 into phases [0, 2) and [2, 3), padding the missing column with zeros.

**Trap to avoid:** Skipping the post-accumulation barrier lets a fast thread overwrite data still being read.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Count phases for \(\mathrm{k}=5\) and tile width two.

**Trap to avoid:** Using floor(5 / 2) = 2 phases drops the fifth product.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is returning early for an out-of-range output thread dangerous?

**Trap to avoid:** Returning early leaves tile slots unloaded and a barrier that some threads never reach.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How much shared storage do two 16-by-16 float tiles use?

**Trap to avoid:** Counting one tile gives 1,024 and underestimates the shared budget per block.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

A tiled kernel loses on a tiny matrix. Is that a bug?

**Trap to avoid:** Calling it a bug and disabling tiling for all sizes discards gains on large shapes.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Shared memory automatically makes a kernel faster.** Shared memory only helps when values are reused enough to repay loading and synchronizing. Tiling adds barriers and uses shared storage that can lower occupancy, and on tiny matrices the overhead dominates. Worked example 1 counts the saved reads; whether that saves time must still be measured.

## Self-check, retrieval and transfer

1. How many phases does k equal 7 need with tile width 4?
2. Why are invalid tile entries filled with zero?
3. Why is a second barrier needed at the end of each phase?

Short answers are in the [separate explanations](../solutions/cuda-019_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
