# cuda-035: Shared-memory banks and a transpose case study

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-015`, `cuda-017`, `cuda-034`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a tiled transpose with correct output and explain the measured effect of the chosen shared-memory layout.

**Scope:** Shared-memory access patterns, bank conflicts, broadcasts, padding, and tiling.

**Evidence to produce:** Correct output and a measured explanation of the selected layout.

## Purpose, vocabulary and mental model

Shared memory is organized into banks. Different lanes accessing different words in the same bank can serialize under the relevant hardware rules, while some same-address reads can broadcast. Global coalescing and shared-bank behavior are different layers. A transpose benefits from loading rows coalesced into a tile and storing columns through a coordinated layout. Padding can alter the bank mapping of columns, but it also changes storage usage and is not a universal speed rule. Use a simplified bank model to reason, then check the actual element width and architecture before treating the model as a performance prediction.

### Key terms

- **Shared memory bank:** One of 32 four-byte-wide divisions of shared memory that can each serve one address per cycle.
- **Bank conflict:** Several lanes of a warp accessing different addresses in the same bank, which serializes the access.
- **Broadcast:** Many lanes reading the same shared-memory word, which is served at once without a conflict.
- **Padding column:** One extra element per tile row, as in `tile[32][33]`, that shifts columns into different banks.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-035_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-035_cpu.py
```

## CUDA C++ kernel listing

The padded tile is the transpose case study's layout. Global reads and writes both stay coalesced through the tile, and the extra column changes each column's bank in the simplified 32-bank model; whether it is faster on a given GPU is a measurement question.

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

**Why:** With width 32 every row lands in bank 0, while width 33 shifts each row by one bank, so 32 rows hit 32 distinct banks.

```python
banks_plain = [(row * 32) % 32 for row in range(32)]
banks_padded = [(row * 33) % 32 for row in range(32)]
assert len(set(banks_plain)) == 1 and len(set(banks_padded)) == 32
matrix = [[1, 2, 3], [4, 5, 6]]
assert list(map(list, zip(*matrix))) == [[1, 4], [2, 5], [3, 6]]
print({"model_unique_banks": [len(set(banks_plain)), len(set(banks_padded))]})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'model_unique_banks': [1, 32]}
```

**Check:** The reference asserts one unique bank for the plain layout and 32 unique banks for the padded layout.

## Worked example 2: change a meaningful condition

Transpose \([[1,2,3],[4,5,6]]\) into \([[1,4],[2,5],[3,6]]\). A tile implementation must preserve this rectangular mapping at edges. Padding is internal storage, so it must not appear as extra output rows or columns.

**Why:** Output row c collects column c of the input, giving [[1, 4], [2, 5], [3, 6]] with three rows of two.

**Check:** The reference asserts list(map(list, zip(*matrix))) == [[1, 4], [2, 5], [3, 6]]; compare shapes as well as values.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Compute bank = (row * width) mod 32 for column reads of a tile with width 32, then repeat with width 33.

**Trap to avoid:** Padding by 32 extra words instead of one leaves (row * 64) mod 32 at zero, keeping every access in bank 0.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Map input (r, c) to output (c, r) for the 2-by-3 matrix and guard each axis of the tile separately.

**Trap to avoid:** Copying the padded 33-wide tile row straight to output writes the padding column as an extra value.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute bank indices for rows 0 through 3 at stride 33 in the model.

**Trap to avoid:** Reusing the width-32 result of bank 0 for every row ignores the extra padding word.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A padded transpose is faster but wrong on width 17. What matters first?

**Trap to avoid:** Keeping the padded kernel because it is faster on aligned sizes ships wrong results for width 17.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Does padding help every access pattern?

**Trap to avoid:** Padding every shared array by default wastes shared capacity and can reduce resident blocks.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the model to double values.

**Trap to avoid:** Copying the float formula with stride 33 assumes one word per element and may mispredict conflicts.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Padding every shared array is universally faster or bank conflicts and global-memory coalescing are the same issue.** Padding changes the shared bank mapping only; worked example 1 shows width 33 spreading a column across banks. It does nothing for global coalescing, and on patterns without conflicts it only wastes shared memory. Treat banks and coalescing as separate layers and measure each.

## Self-check, retrieval and transfer

1. In the 32-bank model, which bank does row 5 of a column use at width 33?
2. Why can a same-address read avoid a conflict?
3. What must a padded transpose never output?

Short answers are in the [separate explanations](../solutions/cuda-035_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
