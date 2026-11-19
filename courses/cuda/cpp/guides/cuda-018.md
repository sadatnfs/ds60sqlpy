# cuda-018: A simple matrix multiplication with a complete specification

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-015`, `cuda-017`, `cuda-006`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *A simple matrix multiplication with a complete specification* with the concrete cases below. Finish with this evidence:
correctness across the shape suite and a transparent operation/byte estimate. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Matrix multiplication contracts a shared dimension: an m-by-k matrix A times a k-by-n matrix B produces an m-by-n matrix C. One simple CUDA thread owns one output coordinate and loops across k. Row-major A uses row*k+inner; row-major B uses inner*n+column. The output uses row*n+column. This deliberately simple kernel rereads data and serves as an understandable correctness baseline. Accumulation type and tolerance are part of its specification. Distinct entries and rectangular shapes reveal layout errors better than square all-ones inputs.

## Mathematical contract

\[
C_{r,c}=\sum_{k=0}^{K-1}A_{r,k}B_{k,c}
\]

Rows r and columns c identify the output, while k is the contracted dimension. Empty contraction has a zero sum under this definition.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-018_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-018_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

This is the baseline kernel the chapter specifies: one thread per output coordinate, explicit row-major offsets and a bounds check before any read. The early return is safe only because the kernel has no barrier. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

```cpp
// One thread computes one C[row, col]. A is M-by-K, B is K-by-N and C is
// M-by-N, all row-major.
__global__ void matmul_naive(const float *A, const float *B, float *C, int M,
                             int N, int K) {
  const int row = blockIdx.y * blockDim.y + threadIdx.y;
  const int col = blockIdx.x * blockDim.x + threadIdx.x;
  if (row >= M || col >= N)
    return; // safe here: no barrier follows
  float sum = 0.0f;
  for (int inner = 0; inner < K; ++inner)
    sum += A[row * K + inner] * B[inner * N + col];
  C[row * N + col] = sum;
}
// Launch: dim3 block(16, 16);
//         dim3 grid((N + 15) / 16, (M + 15) / 16);
```

## Worked example 1: trace the mechanism

Multiply \([[1,2,3],[4,5,6]]\) by \([[1,2],[0,1],[2,0]]\). The output is \([[7,4],[16,13]]\). Entry (1,0) is \(4\times 1+5\times 0+6\times 2=16\). Explicitly name every dimension before translating the three scalar indices into flat offsets.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
A = [[1, 2, 3], [4, 5, 6]]
B = [[1, 2], [0, 1], [2, 0]]
C = [[sum(A[r][k] * B[k][c] for k in range(3)) for c in range(2)] for r in range(2)]
assert C == [[7, 4], [16, 13]]
print(C)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
[[7, 4], [16, 13]]
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Multiplying by an identity matrix preserves input, but that test alone can miss some errors. A 3-by-5 times 5-by-2 case exercises tails and asymmetric dimensions. If \(\mathrm{k}=0\), define the sum of zero products as zero and decide how the host handles the empty inputs without invalid launches.

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

Compute entry (0,1) in the worked product.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

An implementation swaps m and n yet passes a square test. Add a counterexample.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What happens when m or n is zero?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Estimate multiply-add work for \(\mathrm{m}=2\),\(\mathrm{k}=3\),\(\mathrm{n}=2\).

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **passing a square all-ones example establishes layout correctness.**

For the concrete failure exercise, an implementation swaps m and n yet passes a square test. Add a counterexample.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-018_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-018: A simple matrix multiplication with a complete specification.
Read courses/cuda/cpp/guides/cuda-018.md and courses/cuda/cpp/lessons/cuda-018.md.
Direct prerequisites: `cuda-015`, `cuda-017`, `cuda-006`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-018_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-018_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
