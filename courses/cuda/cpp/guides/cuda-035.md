# cuda-035: Shared-memory banks and a transpose case study

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-015`, `cuda-017`, `cuda-034`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Shared-memory banks and a transpose case study* with the concrete cases below. Finish with this evidence:
correct output and a measured explanation of the selected layout. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Shared memory is organized into banks. Different lanes accessing different words in the same bank can serialize under the relevant hardware rules, while some same-address reads can broadcast. Global coalescing and shared-bank behavior are different layers. A transpose benefits from loading rows coalesced into a tile and storing columns through a coordinated layout. Padding can alter the bank mapping of columns, but it also changes storage usage and is not a universal speed rule. Use a simplified bank model to reason, then check the actual element width and architecture before treating the model as a performance prediction.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-035_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-035_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The padded tile is the transpose case study's layout. Global reads and writes both stay coalesced through the tile, and the extra column changes each column's bank in the simplified 32-bank model; whether it is faster on a given GPU is a measurement question. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

```cpp
constexpr int TILE = 32;

// Transpose a rows-by-cols row-major matrix. A warp reads one tile row and
// later writes one output row, so both global accesses stay coalesced. The
// extra column moves each tile column to a different bank in the simplified
// 32-bank model.
__global__ void transpose_tiled(const float *in, float *out, int rows,
                                int cols) {
  __shared__ float tile[TILE][TILE + 1];
  int x = blockIdx.x * TILE + threadIdx.x; // input column
  int y = blockIdx.y * TILE + threadIdx.y; // input row
  if (x < cols && y < rows)
    tile[threadIdx.y][threadIdx.x] = in[y * cols + x];
  __syncthreads(); // the whole tile is loaded before any column is read
  x = blockIdx.y * TILE + threadIdx.x; // output column = input row
  y = blockIdx.x * TILE + threadIdx.y; // output row = input column
  if (x < rows && y < cols)
    out[y * rows + x] = tile[threadIdx.x][threadIdx.y];
}
// Launch: dim3 block(TILE, TILE);
//         dim3 grid((cols + TILE - 1) / TILE, (rows + TILE - 1) / TILE);
```

## Worked example 1: trace the mechanism

In a simplified 32-bank, one-word-per-bank model, a column of a 32-word-wide tile maps every row to bank zero because (row*32) mod 32 is zero. With width 33, row r maps to bank r mod 32. This explains the common padding experiment without promising every architecture uses this exact cost model.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
banks_plain = [(row * 32) % 32 for row in range(32)]
banks_padded = [(row * 33) % 32 for row in range(32)]
assert len(set(banks_plain)) == 1 and len(set(banks_padded)) == 32
matrix = [[1, 2, 3], [4, 5, 6]]
assert list(map(list, zip(*matrix))) == [[1, 4], [2, 5], [3, 6]]
print({"model_unique_banks": [len(set(banks_plain)), len(set(banks_padded))]})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'model_unique_banks': [1, 32]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Transpose \([[1,2,3],[4,5,6]]\) into \([[1,4],[2,5],[3,6]]\). A tile implementation must preserve this rectangular mapping at edges. Padding is internal storage, so it must not appear as extra output rows or columns.

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

Compute bank indices for rows 0 through 3 at stride 33 in the model.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A padded transpose is faster but wrong on width 17. What matters first?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Does padding help every access pattern?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the model to double values.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **padding every shared array is universally faster or bank conflicts and global-memory coalescing are the same issue.**

For the concrete failure exercise, a padded transpose is faster but wrong on width 17. What matters first?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-035_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-035: Shared-memory banks and a transpose case study.
Read courses/cuda/cpp/guides/cuda-035.md and courses/cuda/cpp/lessons/cuda-035.md.
Direct prerequisites: `cuda-015`, `cuda-017`, `cuda-034`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-035_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-035_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
