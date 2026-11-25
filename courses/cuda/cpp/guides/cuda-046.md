# cuda-046: cuBLAS and cuBLASLt without layout confusion

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-018`, `cuda-029`, `cuda-039`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Call cuBLAS GEMM with correct column-major shapes and leading dimensions and compare it fairly, including setup.

**Scope:** GEMM parameters, leading dimensions, transpose flags, handles, streams, accumulation types, batching, workspace and algorithm selection.

**Evidence to produce:** Correct shapes/layouts and a fair comparison including setup where relevant.

## Purpose, vocabulary and mental model

GEMM computes scaled matrix multiplication plus an existing output contribution. In conventional notation, C becomes alpha times A*B plus beta times C. Classic cuBLAS uses column-major conventions, so leading dimensions and transpose flags must be interpreted accordingly. cuBLASLt provides more explicit layout and algorithm descriptors, with workspace and compute-type choices. A handle has lifecycle and stream configuration. Check library status separately from CUDA completion. A successful call with wrong dimensions can produce plausible but incorrect data, especially when symmetric inputs conceal transposition mistakes.

### Key terms

- **Column-major order:** A storage order in which each column is contiguous, which cuBLAS assumes by default.
- **Leading dimension:** The stride in elements between consecutive columns of a column-major matrix in cuBLAS.
- **Transpose flag:** An operation argument such as `CUBLAS_OP_T` that tells cuBLAS to use a matrix transposed without copying it.
- **cuBLAS handle:** A library context created once and reused, which owns workspace and stream settings.
- **Alpha and beta:** Scalars in C = alpha * op(A) * op(B) + beta * C, where a nonzero beta reads the existing C.

## Mathematical contract

\[
C\leftarrow\alpha A B+\beta C
\]

Dimensions, layout and compute type must match the selected GEMM interface. The old output contributes when beta is nonzero.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-046_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-046_cpu.py
```

## Worked example 1: trace the mechanism

Use the rectangular A and B from cuda-018, whose product is \([[7,4],[16,13]]\). With \(\alpha=2\), \(\beta=3\) and initial C all ones, the result becomes \([[17,11],[35,29]]\). This catches implementations that ignore beta or assume the output is initially zero.

**Why:** The product [[7, 4], [16, 13]] doubles to [[14, 8], [32, 26]], and adding 3 to every entry gives [[17, 11], [35, 29]].

```python
product = [[7, 4], [16, 13]]
result = [[2 * x + 3 for x in row] for row in product]
assert result == [[17, 11], [35, 29]]
A = [[1, 2, 3], [4, 5, 6]]
column_major = [A[r][c] for c in range(3) for r in range(2)]
assert column_major == [1, 4, 2, 5, 3, 6]
print({"scaled_GEMM": result, "column_major": column_major})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'scaled_GEMM': [[17, 11], [35, 29]], 'column_major': [1, 4, 2, 5, 3, 6]}
```

**Check:** The reference asserts result == [[17, 11], [35, 29]]; on a GPU initialize C to ones explicitly before the call.

## Worked example 2: change a meaningful condition

For column-major storage, a 2-by-3 matrix \([[1,2,3],[4,5,6]]\) is flattened \([1,4,2,5,3,6]\), with leading dimension two. Row-major flattening is \([1,2,3,4,5,6]\). Passing one while describing the other changes the interpretation rather than merely the speed.

**Why:** Column-major order stores each column contiguously, so the leading dimension equals the row count.

**Check:** The reference asserts column_major == [1, 4, 2, 5, 3, 6]; compare a cuBLAS result against the host product for this matrix.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Compute alpha times A times B plus beta times C with alpha 2, beta 3 and C initialized to ones.

**Trap to avoid:** Ignoring beta returns [[14, 8], [32, 26]], and assuming C starts at zero hides that mistake on a fresh buffer.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Flatten the 2-by-3 matrix by columns to [1, 4, 2, 5, 3, 6] with leading dimension 2.

**Trap to avoid:** Passing the row-major buffer [1, 2, 3, 4, 5, 6] while declaring column-major makes the library read a different 2-by-3 matrix with no error.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute the result when \(\alpha=0\) and \(\beta=2\) for initial C=\([[1,3],[2,4]]\).

**Trap to avoid:** Skipping the call entirely when alpha is zero leaves C unscaled at [[1, 3], [2, 4]].

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is swapping dimensions until a test passes unsafe?

**Trap to avoid:** Swapping m, n or transpose flags until a square test passes can leave the layout wrong in every other shape.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should \(\beta=0\) mean mathematically?

**Trap to avoid:** Leaving C uninitialized and assuming that is fine without checking the library contract may propagate NaN in some implementations.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a fair handwritten-versus-library comparison.

**Trap to avoid:** Comparing a handwritten float kernel with a library double call compares different work.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Swapping dimensions until a test passes is an acceptable layout strategy.** Swapping dimensions until one test passes can coincide with a transposed or wrongly strided interpretation that fails on other shapes. Worked example 2 shows the same values flattened differently in column-major and row-major order. Write the layout, leading dimension and transpose flags for each operand first, then test rectangular shapes.

## Self-check, retrieval and transfer

1. What is the leading dimension of a column-major 3-by-4 matrix without padding?
2. Why does worked example 1 use beta equal to 3 with C initialized to ones?
3. What should beta equal to 0 mean?

Short answers are in the [separate explanations](../solutions/cuda-046_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
