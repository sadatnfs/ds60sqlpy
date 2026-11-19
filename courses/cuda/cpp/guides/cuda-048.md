# cuda-048: cuSPARSE and sparsity as a data structure

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`, `cuda-018`, `cuda-037`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *cuSPARSE and sparsity as a data structure* with the concrete cases below. Finish with this evidence:
correct result and a reasoned choice considering conversion, reuse and distribution. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Sparse storage represents selected entries and their coordinates instead of storing every zero. Compressed sparse row, CSR, stores row offsets, column indices and values. Row offsets delimit each row's entries; the final offset equals the stored-entry count. Specify index base, sortedness and duplicate handling. A sparse multiply can save arithmetic and storage but introduces indirect reads and uneven row work. Conversion and preprocessing costs matter, especially for one-shot operations. Arbitrary sparsity is different from structured sparsity supported by certain hardware/library modes.

## Mathematical contract

\[
y_r=\sum_{j=\mathrm{rowptr}[r]}^{\mathrm{rowptr}[r+1]-1}\mathrm{value}[j]x_{\mathrm{column}[j]}
\]

Offsets and columns here are zero-based. Empty rows have equal adjacent offsets and therefore an empty sum.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-048_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-048_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Matrix \([[2,0,1],[0,3,0]]\) has CSR offsets \([0,2,3]\), columns \([0,2,1]\) and values \([2,1,3]\). Multiplying by \([4,5,6]\) gives \([14,15]\). The first row reads two entries; the second reads one. Offsets are boundaries, not per-row counts.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
offsets, columns, values = [0, 2, 3], [0, 2, 1], [2, 1, 3]
x = [4, 5, 6]
y = [sum(values[j] * x[columns[j]] for j in range(offsets[r], offsets[r + 1])) for r in range(2)]
assert y == [14, 15]
assert offsets[-1] == len(values) == len(columns)
print({"CSR_product": y, "row_lengths": [offsets[i + 1] - offsets[i] for i in range(2)]})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'CSR_product': [14, 15], 'row_lengths': [2, 1]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

An empty middle row repeats an offset. For lengths \([2,0,1]\), row boundaries are \([0,2,2,3]\). Repeated offsets are valid. A descending offset or a column outside the matrix width is invalid and must be rejected before device access.

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

Build CSR row offsets from row lengths \([0,1,3]\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can 90% zeros still fail to improve runtime?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Define duplicate-coordinate handling.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer CSR to graph aggregation.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a matrix containing many zero values is automatically stored sparsely or always runs faster. .**

For the concrete failure exercise, why can 90% zeros still fail to improve runtime?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-048_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
