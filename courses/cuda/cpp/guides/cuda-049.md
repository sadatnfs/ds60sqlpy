# cuda-049: cuSOLVER, conditioning and robust linear algebra

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-029`, `cuda-046`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain cuSOLVER, conditioning and robust linear algebra using the concrete cases below. Produce checked solver status, residual report and a numerically justified interpretation.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

A linear solver seeks x such that A*x approximates b. Factorization usually avoids the unnecessary work and numerical costs of explicitly constructing an inverse. Library status tells whether the requested procedure completed; a residual checks how well the returned vector satisfies the equation. A small residual does not guarantee a small error in x when A is ill-conditioned, meaning small input changes can greatly change the solution. Report both the residual and a conditioning interpretation. Workspace, matrix layout, pivoting and rank assumptions belong to the solver contract rather than being incidental implementation details.

## Mathematical contract

\[
r=b-A\widehat x
\]

The residual r measures equation satisfaction by the computed x-hat. Small residual alone does not imply small forward error for an ill-conditioned matrix.

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
The separate [CPU reference](../references/cuda-049_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-049_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

For A=\([[3,1],[1,2]]\) and b=\([9,8]\), x=\([2,3]\) gives A*x=\([9,8]\), so residual is zero in this exact fixture. This is a good first layout and status test, but it does not exercise singular or poorly conditioned problems.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
A, b, x = [[3, 1], [1, 2]], [9, 8], [2, 3]
product = [sum(a * v for a, v in zip(row, x)) for row in A]
residual = [rhs - value for rhs, value in zip(b, product)]
assert residual == [0, 0]
wrong = [sum(a * v for a, v in zip(row, [2, 2])) for row in A]
assert [rhs - value for rhs, value in zip(b, wrong)] == [1, 2]
print({"solution": x, "residual": residual})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'solution': [2, 3], 'residual': [0, 0]}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For A=\([[1,1],[1,1.000001]]\), small changes in the second component of b can produce large changes in the two components of x. The nearly dependent rows provide little independent information. A solver returning numbers cannot remove that uncertainty; inspect conditioning and the problem specification.

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

Compute the residual for candidate x=\([2,2]\) in the first system.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

Why avoid solving by explicitly computing A inverse?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What should a singular-matrix status produce?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Transfer the idea to least squares.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **obtaining a vector from a solver proves that the original problem was well-posed. .**

For the concrete failure exercise, why avoid solving by explicitly computing A inverse?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-049_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [cuSOLVER documentation](https://docs.nvidia.com/cuda/cusolver/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-049: cuSOLVER, conditioning and robust linear algebra.
Read courses/cuda/cpp/guides/cuda-049.md and courses/cuda/cpp/lessons/cuda-049.md.
Direct prerequisites: `cuda-006`, `cuda-029`, `cuda-046`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-049_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-049_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
