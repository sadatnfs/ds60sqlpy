# cuda-018: A simple matrix multiplication with a complete specification

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-015`, `cuda-017`, `cuda-006`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Verify a one-thread-per-output matrix multiplication across a rectangular shape suite and estimate its operations and bytes.

**Scope:** Matrix dimensions, contraction, row-major offsets, accumulation type and numerical tolerance.

**Evidence to produce:** Correctness across the shape suite and a transparent operation/byte estimate.

## Purpose, vocabulary and mental model

Matrix multiplication contracts a shared dimension: an m-by-k matrix A times a k-by-n matrix B produces an m-by-n matrix C. One simple CUDA thread owns one output coordinate and loops across k. Row-major A uses row*k+inner; row-major B uses inner*n+column. The output uses row*n+column. This deliberately simple kernel rereads data and serves as an understandable correctness baseline. Accumulation type and tolerance are part of its specification. Distinct entries and rectangular shapes reveal layout errors better than square all-ones inputs.

### Key terms

- **GEMM:** General matrix multiplication, which produces an m-by-n result from m-by-k and k-by-n inputs.
- **Shared dimension:** The inner dimension k that is summed over when multiplying A by B.
- **Accumulation type:** The precision used for the running sum of products, which can differ from the input type.
- **Correctness baseline:** A simple, readable implementation used as the trusted reference for faster versions.

## Mathematical contract

\[
C_{r,c}=\sum_{k=0}^{K-1}A_{r,k}B_{k,c}
\]

Rows r and columns c identify the output, while k is the contracted dimension. Empty contraction has a zero sum under this definition.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-018_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-018_cpu.py
```

## CUDA C++ kernel listing

This is the baseline kernel the chapter specifies: one thread per output coordinate, explicit row-major offsets and a bounds check before any read. The early return is safe only because the kernel has no barrier.

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

**Why:** Entry (1, 0) pairs row 1 of A with column 0 of B: 4 + 0 + 12 = 16.

```python
A = [[1, 2, 3], [4, 5, 6]]
B = [[1, 2], [0, 1], [2, 0]]
C = [[sum(A[r][k] * B[k][c] for k in range(3)) for c in range(2)] for r in range(2)]
assert C == [[7, 4], [16, 13]]
print(C)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
[[7, 4], [16, 13]]
```

**Check:** The reference asserts C == [[7, 4], [16, 13]].

## Worked example 2: change a meaningful condition

Multiplying by an identity matrix preserves input, but that test alone can miss some errors. A 3-by-5 times 5-by-2 case exercises tails and asymmetric dimensions. If \(\mathrm{k}=0\), define the sum of zero products as zero and decide how the host handles the empty inputs without invalid launches.

**Why:** Unequal dimensions catch swapped strides that a square identity case tolerates.

**Check:** Compare every entry of the 3-by-2 output with the host triple loop.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Name m = 2, k = 3, n = 2, then compute each C[r][c] as a sum over k.

**Trap to avoid:** Indexing B as B[c][k] uses rows of B instead of columns and gives wrong entries.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Add a 3-by-5 times 5-by-2 fixture with distinct values beside the identity test.

**Trap to avoid:** Relying on identity multiplication lets an implementation that transposes B still pass.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute entry (0,1) in the worked product.

**Trap to avoid:** Summing across output columns instead of k adds unrelated products.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

An implementation swaps m and n yet passes a square test. Add a counterexample.

**Trap to avoid:** Adding more square tests of other sizes never distinguishes m from n.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What happens when m or n is zero?

**Trap to avoid:** Launching with ceil(0 / 16) blocks still produces an invalid configuration.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Estimate multiply-add work for \(\mathrm{m}=2\),\(\mathrm{k}=3\),\(\mathrm{n}=2\).

**Trap to avoid:** Counting only m * n = 4 outputs understates work by the factor k.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Passing a square all-ones example establishes layout correctness.** A square all-ones input yields the same output under swapped indices or transposed layouts, so layout mistakes cannot appear. Worked example 2 recommends a 3-by-5 times 5-by-2 product with distinct values, which makes swapped m and n or wrong offsets produce visibly wrong entries.

## Self-check, retrieval and transfer

1. Give the flat offset of A(1,2) when A is 2-by-3 row-major.
2. How many multiply-adds does an m-by-k times k-by-n product need?
3. Why record the accumulation type with the test?

Short answers are in the [separate explanations](../solutions/cuda-018_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
