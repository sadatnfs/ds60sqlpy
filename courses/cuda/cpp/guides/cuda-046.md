# cuda-046: cuBLAS and cuBLASLt without layout confusion

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-018`, `cuda-029`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *cuBLAS and cuBLASLt without layout confusion* with the concrete cases below. Finish with this evidence:
correct shapes/layouts and a fair comparison including setup where relevant. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

GEMM computes scaled matrix multiplication plus an existing output contribution. In conventional notation, C becomes alpha times A*B plus beta times C. Classic cuBLAS uses column-major conventions, so leading dimensions and transpose flags must be interpreted accordingly. cuBLASLt provides more explicit layout and algorithm descriptors, with workspace and compute-type choices. A handle has lifecycle and stream configuration. Check library status separately from CUDA completion. A successful call with wrong dimensions can produce plausible but incorrect data, especially when symmetric inputs conceal transposition mistakes.

## Mathematical contract

\[
C\leftarrow\alpha A B+\beta C
\]

Dimensions, layout and compute type must match the selected GEMM interface. The old output contributes when beta is nonzero.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-046_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-046_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Use the rectangular A and B from cuda-018, whose product is \([[7,4],[16,13]]\). With \(\alpha=2\), \(\beta=3\) and initial C all ones, the result becomes \([[17,11],[35,29]]\). This catches implementations that ignore beta or assume the output is initially zero.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
product = [[7, 4], [16, 13]]
result = [[2 * x + 3 for x in row] for row in product]
assert result == [[17, 11], [35, 29]]
A = [[1, 2, 3], [4, 5, 6]]
column_major = [A[r][c] for c in range(3) for r in range(2)]
assert column_major == [1, 4, 2, 5, 3, 6]
print({"scaled_GEMM": result, "column_major": column_major})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'scaled_GEMM': [[17, 11], [35, 29]], 'column_major': [1, 4, 2, 5, 3, 6]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For column-major storage, a 2-by-3 matrix \([[1,2,3],[4,5,6]]\) is flattened \([1,4,2,5,3,6]\), with leading dimension two. Row-major flattening is \([1,2,3,4,5,6]\). Passing one while describing the other changes the interpretation rather than merely the speed.

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

Compute the result when \(\alpha=0\) and \(\beta=2\) for initial C=\([[1,3],[2,4]]\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is swapping dimensions until a test passes unsafe?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should \(\beta=0\) mean mathematically?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a fair handwritten-versus-library comparison.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **swapping dimensions until a test passes is an acceptable layout strategy. .**

For the concrete failure exercise, why is swapping dimensions until a test passes unsafe?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-046_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [cuBLAS documentation](https://docs.nvidia.com/cuda/cublas/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-046: cuBLAS and cuBLASLt without layout confusion.
Read courses/cuda/cpp/guides/cuda-046.md and courses/cuda/cpp/lessons/cuda-046.md.
Direct prerequisites: `cuda-018`, `cuda-029`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-046_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-046_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
