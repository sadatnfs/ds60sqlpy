# cuda-049: explanatory solutions

## Mechanism review

A linear solver seeks x such that A*x approximates b. Factorization usually avoids the unnecessary work and numerical costs of explicitly constructing an inverse. Library status tells whether the requested procedure completed; a residual checks how well the returned vector satisfies the equation. A small residual does not guarantee a small error in x when A is ill-conditioned, meaning small input changes can greatly change the solution. Report both the residual and a conditioning interpretation. Workspace, matrix layout, pivoting and rank assumptions belong to the solver contract rather than being incidental implementation details.

## Exercise 1

For A=\([[3,1],[1,2]]\) and b=\([9,8]\), x=\([2,3]\) gives A*x=\([9,8]\), so residual is zero in this exact fixture. This is a good first layout and status test, but it does not exercise singular or poorly conditioned problems.

**Approach:** Solve A = [[3, 1], [1, 2]] against b = [9, 8] with a factorization routine, then compute b minus A times x.

**Why it is correct:** x = [2, 3] gives 3 * 2 + 3 = 9 and 2 + 2 * 3 = 8, so the residual is exactly [0, 0].

**A plausible wrong approach:** Passing the row-major A to a column-major solver solves the transpose, which here is the same symmetric matrix and hides the bug.

**How to verify:** The reference asserts residual == [0, 0]; add a nonsymmetric fixture so a layout error changes the answer.

## Exercise 2

For A=\([[1,1],[1,1.000001]]\), small changes in the second component of b can produce large changes in the two components of x. The nearly dependent rows provide little independent information. A solver returning numbers cannot remove that uncertainty; inspect conditioning and the problem specification.

**Approach:** Perturb the second entry of b slightly for A = [[1, 1], [1, 1.000001]] and compare the two solutions.

**Why it is correct:** The rows are nearly parallel, so the condition number is large and tiny data changes swing x widely.

**A plausible wrong approach:** Reporting the solver's x to many digits as if it were precise ignores that the problem itself is unstable.

**How to verify:** Compute the condition number and report it with the residual and the solution change under perturbation.

## Exercise 3

A*x=\([8,6]\), so b-A*x=\([1,2]\). A successful API status cannot excuse this wrong result.

**Approach:** Multiply A by [2, 2] to get [8, 6] and subtract from [9, 8].

**Why it is correct:** The residual [1, 2] is nonzero, so [2, 2] does not solve the system.

**A plausible wrong approach:** Trusting a success status from the solver call without checking the residual accepts this wrong answer.

**How to verify:** The reference asserts the residual of [2, 2] equals [1, 2].

## Exercise 4

A factorization-based solve generally does less unnecessary work and can use better numerical procedures; an explicit inverse is not required for the stated task.

**Approach:** Factor A once and use triangular solves instead of forming A inverse.

**Why it is correct:** Factorization does less work and gives better rounding behavior for the same answer.

**A plausible wrong approach:** Computing the inverse and multiplying by b adds work and amplifies error on ill-conditioned input.

**How to verify:** Compare residuals from both approaches on the nearly singular matrix.

## Exercise 5

A named failure or alternate documented rank-aware method, never a fabricated successful solution.

**Approach:** Return a named singular-matrix failure or switch to a documented rank-aware method.

**Why it is correct:** A singular system has no unique solution to report.

**A plausible wrong approach:** Returning whatever numbers the factorization left in the buffer fabricates a solution.

**How to verify:** Pass [[1, 1], [1, 1]] and assert the failure status or rank-aware result.

## Exercise 6

State rank and scaling assumptions, compare a suitable factorization method and report residual plus uncertainty/conditioning rather than only coefficient values.

**Approach:** State rank and scaling assumptions, use a QR or similar solve, and report residual and conditioning.

**Why it is correct:** Least squares minimizes the residual, so its size is part of the answer.

**A plausible wrong approach:** Solving the normal equations by default squares the condition number.

**How to verify:** Compare QR and normal-equation residuals on a poorly scaled design matrix.

## Self-check answers

1. **What is the residual of x = [2,3] in worked example 1?** Zero, because A times x equals b exactly.
2. **Why prefer factorization over computing the inverse?** It is cheaper and numerically more stable for solving.
3. **What does an ill-conditioned matrix mean for the answer?** Small input changes can cause large changes in x, so errors in b are amplified.

## Numerical reference and its limits

The [CPU reference](../references/cuda-049_cpu.py) reproduces worked example 1 and prints `{'solution': [2, 3], 'residual': [0, 0]}`.

## Transfer review

State rank and scaling assumptions, compare a suitable factorization method and report residual plus uncertainty/conditioning rather than only coefficient values.
