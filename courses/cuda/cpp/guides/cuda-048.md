# cuda-048: cuSPARSE and sparsity as a data structure

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`, `cuda-018`, `cuda-037`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Build a CSR matrix and decide whether sparse storage pays off after conversion, reuse and row distribution.

**Scope:** CSR/COO representations, index bases, duplicates, irregular rows, format conversion, fill ratio and preprocessing cost.

**Evidence to produce:** Correct result and a reasoned choice considering conversion, reuse and distribution.

## Purpose, vocabulary and mental model

Sparse storage represents selected entries and their coordinates instead of storing every zero. Compressed sparse row, CSR, stores row offsets, column indices and values. Row offsets delimit each row's entries; the final offset equals the stored-entry count. Specify index base, sortedness and duplicate handling. A sparse multiply can save arithmetic and storage but introduces indirect reads and uneven row work. Conversion and preprocessing costs matter, especially for one-shot operations. Arbitrary sparsity is different from structured sparsity supported by certain hardware/library modes.

### Key terms

- **CSR format:** Compressed sparse row storage made of values, column indices and row offsets.
- **Row offsets:** An array of length rows+1 whose consecutive entries bound each row's range of stored nonzeros.
- **Sparsity:** The fraction of matrix entries that are zero, which alone does not decide whether sparse storage is faster.
- **SpMV:** Sparse matrix-vector multiplication, often limited by irregular memory access and row length imbalance.

## Mathematical contract

\[
y_r=\sum_{j=\mathrm{rowptr}[r]}^{\mathrm{rowptr}[r+1]-1}\mathrm{value}[j]x_{\mathrm{column}[j]}
\]

Offsets and columns here are zero-based. Empty rows have equal adjacent offsets and therefore an empty sum.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-048_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-048_cpu.py
```

## Worked example 1: trace the mechanism

Matrix \([[2,0,1],[0,3,0]]\) has CSR offsets \([0,2,3]\), columns \([0,2,1]\) and values \([2,1,3]\). Multiplying by \([4,5,6]\) gives \([14,15]\). The first row reads two entries; the second reads one. Offsets are boundaries, not per-row counts.

**Why:** Row 0 spans entries 0 to 2: 2 times x[0] = 8 plus 1 times x[2] = 6 gives 14; row 1 has 3 times x[1] = 15.

```python
offsets, columns, values = [0, 2, 3], [0, 2, 1], [2, 1, 3]
x = [4, 5, 6]
y = [sum(values[j] * x[columns[j]] for j in range(offsets[r], offsets[r + 1])) for r in range(2)]
assert y == [14, 15]
assert offsets[-1] == len(values) == len(columns)
print({"CSR_product": y, "row_lengths": [offsets[i + 1] - offsets[i] for i in range(2)]})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'CSR_product': [14, 15], 'row_lengths': [2, 1]}
```

**Check:** The reference asserts y == [14, 15] and that the final offset equals len(values) and len(columns).

## Worked example 2: change a meaningful condition

An empty middle row repeats an offset. For lengths \([2,0,1]\), row boundaries are \([0,2,2,3]\). Repeated offsets are valid. A descending offset or a column outside the matrix width is invalid and must be rejected before device access.

**Why:** The repeated 2 marks an empty middle row whose span [2, 2) holds nothing.

**Check:** Check offsets never decrease, every column is below the width, and the last offset equals the entry count.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Store [[2, 0, 1], [0, 3, 0]] as offsets [0, 2, 3], columns [0, 2, 1] and values [2, 1, 3], then sum per row.

**Trap to avoid:** Treating offsets as row lengths makes row 0 read zero entries and row 1 read two, scrambling the products.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Exclusive scan the lengths [2, 0, 1] and append the total, giving [0, 2, 2, 3], then validate offsets and columns.

**Trap to avoid:** Rejecting repeated offsets as corrupt refuses a valid matrix with an empty row.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Build CSR row offsets from row lengths \([0,1,3]\).

**Trap to avoid:** Using the inclusive scan [0, 1, 4] as offsets loses the leading zero, so row 1 would appear to start at entry 1.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can 90% zeros still fail to improve runtime?

**Trap to avoid:** Assuming 90 percent zeros means ten times faster ignores overhead per stored entry and small sizes.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Define duplicate-coordinate handling.

**Trap to avoid:** Assuming the library sums duplicates may silently keep one value or fail validation.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer CSR to graph aggregation.

**Trap to avoid:** Mixing source and destination orientation aggregates along reversed edges.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A matrix containing many zero values is automatically stored sparsely or always runs faster.** Dense storage keeps every zero; sparse formats must be chosen and built deliberately. Sparse kernels add indirect reads and uneven row work, so moderate sparsity may run slower than a dense routine. Conversion cost also counts unless the sparse form is reused.

## Self-check, retrieval and transfer

1. What CSR offsets correspond to row lengths [1,0,2]?
2. What does the final CSR offset equal?
3. Name two inputs that must be rejected before device access.

Short answers are in the [separate explanations](../solutions/cuda-048_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [cuSPARSE documentation](https://docs.nvidia.com/cuda/cusparse/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-048: cuSPARSE and sparsity as a data structure.
Read courses/cuda/cpp/guides/cuda-048.md and courses/cuda/cpp/lessons/cuda-048.md.
Direct prerequisites: `cuda-005`, `cuda-018`, `cuda-037`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-048_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-048_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
