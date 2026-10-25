# cuda-018: A simple matrix multiplication with a complete specification

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-015`, `cuda-017`, `cuda-006`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain a simple matrix multiplication with a complete specification using the concrete cases below. Produce correctness across the shape suite and a transparent operation/byte estimate.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

Matrix multiplication contracts a shared dimension: an m-by-k matrix A times a k-by-n matrix B produces an m-by-n matrix C. One simple CUDA thread owns one output coordinate and loops across k. Row-major A uses row*k+inner; row-major B uses inner*n+column. The output uses row*n+column. This deliberately simple kernel rereads data and serves as an understandable correctness baseline. Accumulation type and tolerance are part of its specification. Distinct entries and rectangular shapes reveal layout errors better than square all-ones inputs.

## Mathematical contract

\[
C_{r,c}=\sum_{k=0}^{K-1}A_{r,k}B_{k,c}
\]

Rows r and columns c identify the output, while k is the contracted dimension. Empty contraction has a zero sum under this definition.

## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/cuda-018_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-018_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Multiplying by an identity matrix preserves input, but that test alone can miss some errors. A 3-by-5 times 5-by-2 case exercises tails and asymmetric dimensions. If \(\mathrm{k}=0\), define the sum of zero products as zero and decide how the host handles the empty inputs without invalid launches.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Start with the literal input and intermediate quantities in worked example 1.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Identify exactly which condition changes in worked example 2.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 3

Compute entry (0,1) in the worked product.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

An implementation swaps m and n yet passes a square test. Add a counterexample.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What happens when m or n is zero?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Estimate multiply-add work for \(\mathrm{m}=2\),\(\mathrm{k}=3\),\(\mathrm{n}=2\).

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **passing a square all-ones example establishes layout correctness.**

For the concrete failure exercise, an implementation swaps m and n yet passes a square test. Add a counterexample.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-018_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
