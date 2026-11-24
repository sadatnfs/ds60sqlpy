# cuda-049: cuSOLVER, conditioning and robust linear algebra

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-029`, `cuda-046`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Check solver status and report residual and condition estimates to interpret the accuracy of a linear solve.

Work through *cuSOLVER, conditioning and robust linear algebra* with the concrete cases below. Finish with this evidence:
checked solver status, residual report and a numerically justified interpretation. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A linear solver seeks x such that A*x approximates b. Factorization usually avoids the unnecessary work and numerical costs of explicitly constructing an inverse. Library status tells whether the requested procedure completed; a residual checks how well the returned vector satisfies the equation. A small residual does not guarantee a small error in x when A is ill-conditioned, meaning small input changes can greatly change the solution. Report both the residual and a conditioning interpretation. Workspace, matrix layout, pivoting and rank assumptions belong to the solver contract rather than being incidental implementation details.

### Key terms

- **Factorization:** A decomposition such as LU or Cholesky that turns one solve into simpler triangular solves.
- **Residual:** The vector b - Ax for a computed x, which measures how well the equation is satisfied.
- **Condition number:** A measure of how much relative input error can be amplified in the solution.
- **devInfo:** A device integer that cuSOLVER sets to report invalid parameters or a singular factorization.

## Mathematical contract

\[
r=b-A\widehat x
\]

The residual r measures equation satisfaction by the computed x-hat. Small residual alone does not imply small forward error for an ill-conditioned matrix.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-049_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-049_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

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

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For A=\([[1,1],[1,1.000001]]\), small changes in the second component of b can produce large changes in the two components of x. The nearly dependent rows provide little independent information. A solver returning numbers cannot remove that uncertainty; inspect conditioning and the problem specification.

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

Compute the residual for candidate x=\([2,2]\) in the first system.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why avoid solving by explicitly computing A inverse?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should a singular-matrix status produce?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the idea to least squares.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **obtaining a vector from a solver proves that the original problem was well-posed. .**

For the concrete failure exercise, why avoid solving by explicitly computing A inverse?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-049_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
