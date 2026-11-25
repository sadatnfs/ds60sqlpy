# cuda-049: cuSOLVER, conditioning and robust linear algebra

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-029`, `cuda-046`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Check solver status and report residual and condition estimates to interpret the accuracy of a linear solve.

**Scope:** Factorization versus explicit inversion, solver status, workspace, residuals, rank and conditioning.

**Evidence to produce:** Checked solver status, residual report and a numerically justified interpretation.

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

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-049_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-049_cpu.py
```

## Worked example 1: trace the mechanism

For A=\([[3,1],[1,2]]\) and b=\([9,8]\), x=\([2,3]\) gives A*x=\([9,8]\), so residual is zero in this exact fixture. This is a good first layout and status test, but it does not exercise singular or poorly conditioned problems.

**Why:** x = [2, 3] gives 3 * 2 + 3 = 9 and 2 + 2 * 3 = 8, so the residual is exactly [0, 0].

```python
A, b, x = [[3, 1], [1, 2]], [9, 8], [2, 3]
product = [sum(a * v for a, v in zip(row, x)) for row in A]
residual = [rhs - value for rhs, value in zip(b, product)]
assert residual == [0, 0]
wrong = [sum(a * v for a, v in zip(row, [2, 2])) for row in A]
assert [rhs - value for rhs, value in zip(b, wrong)] == [1, 2]
print({"solution": x, "residual": residual})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'solution': [2, 3], 'residual': [0, 0]}
```

**Check:** The reference asserts residual == [0, 0]; add a nonsymmetric fixture so a layout error changes the answer.

## Worked example 2: change a meaningful condition

For A=\([[1,1],[1,1.000001]]\), small changes in the second component of b can produce large changes in the two components of x. The nearly dependent rows provide little independent information. A solver returning numbers cannot remove that uncertainty; inspect conditioning and the problem specification.

**Why:** The rows are nearly parallel, so the condition number is large and tiny data changes swing x widely.

**Check:** Compute the condition number and report it with the residual and the solution change under perturbation.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Solve A = [[3, 1], [1, 2]] against b = [9, 8] with a factorization routine, then compute b minus A times x.

**Trap to avoid:** Passing the row-major A to a column-major solver solves the transpose, which here is the same symmetric matrix and hides the bug.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Perturb the second entry of b slightly for A = [[1, 1], [1, 1.000001]] and compare the two solutions.

**Trap to avoid:** Reporting the solver's x to many digits as if it were precise ignores that the problem itself is unstable.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute the residual for candidate x=\([2,2]\) in the first system.

**Trap to avoid:** Trusting a success status from the solver call without checking the residual accepts this wrong answer.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why avoid solving by explicitly computing A inverse?

**Trap to avoid:** Computing the inverse and multiplying by b adds work and amplifies error on ill-conditioned input.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should a singular-matrix status produce?

**Trap to avoid:** Returning whatever numbers the factorization left in the buffer fabricates a solution.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the idea to least squares.

**Trap to avoid:** Solving the normal equations by default squares the condition number.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Obtaining a vector from a solver proves that the original problem was well-posed.** A solver returns numbers even when the problem is nearly singular. Check the status, compute the residual and consider conditioning: worked example 2 shows nearly dependent rows where tiny changes in b swing x widely. A small residual then does not mean an accurate x.

## Self-check, retrieval and transfer

1. What is the residual of x = [2,3] in worked example 1?
2. Why prefer factorization over computing the inverse?
3. What does an ill-conditioned matrix mean for the answer?

Short answers are in the [separate explanations](../solutions/cuda-049_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
