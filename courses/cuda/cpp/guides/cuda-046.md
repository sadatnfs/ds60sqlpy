# cuda-046: cuBLAS and cuBLASLt without layout confusion

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-018`, `cuda-029`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain cuBLAS and cuBLASLt without layout confusion using the concrete cases below. Produce correct shapes/layouts and a fair comparison including setup where relevant.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

GEMM computes scaled matrix multiplication plus an existing output contribution. In conventional notation, C becomes alpha times A*B plus beta times C. Classic cuBLAS uses column-major conventions, so leading dimensions and transpose flags must be interpreted accordingly. cuBLASLt provides more explicit layout and algorithm descriptors, with workspace and compute-type choices. A handle has lifecycle and stream configuration. Check library status separately from CUDA completion. A successful call with wrong dimensions can produce plausible but incorrect data, especially when symmetric inputs conceal transposition mistakes.

## Mathematical contract

\[
C\leftarrow\alpha A B+\beta C
\]

Dimensions, layout and compute type must match the selected GEMM interface. The old output contributes when beta is nonzero.

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
The separate [CPU reference](../references/cuda-046_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-046_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For column-major storage, a 2-by-3 matrix \([[1,2,3],[4,5,6]]\) is flattened \([1,4,2,5,3,6]\), with leading dimension two. Row-major flattening is \([1,2,3,4,5,6]\). Passing one while describing the other changes the interpretation rather than merely the speed.

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

Compute the result when \(\alpha=0\) and \(\beta=2\) for initial C=\([[1,3],[2,4]]\).

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

Why is swapping dimensions until a test passes unsafe?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What should \(\beta=0\) mean mathematically?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Design a fair handwritten-versus-library comparison.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **swapping dimensions until a test passes is an acceptable layout strategy. .**

For the concrete failure exercise, why is swapping dimensions until a test passes unsafe?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-046_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
