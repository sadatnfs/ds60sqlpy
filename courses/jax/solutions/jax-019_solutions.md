# jax-019: explained reference

Differentiating \(A(\theta)x(\theta)=b(\theta)\) gives \(A\,dx/db=I\) when only b varies, and \(dx/d\theta=A^{-1}(db/d\theta-(dA/d\theta)x)\). This identity describes a solve, not a recommendation to form an inverse. For \(A=\operatorname{diag}(2+\theta,3)\), \(b=(2,6)\), the solution is \((2/(2+\theta),2)\). At zero, the derivative of its summed coordinates is \(-1/2\).

## Solution approach

Solve the 2 by 2 system by hand once: A = [[3, 1], [1, 2]] has determinant 5 and inverse [[2, -1], [-1, 3]] / 5. Every value in the tasks follows from that inverse, from the closed form `x1 = 2 / (2 + theta)` for the diagonal system, or from the scalar ridge formula `x'y / (x'x + lambda)`. Validation stays on the host with a condition-number policy.

**Why it is correct here:** The inverse times [4, 3] gives (8 - 3, -4 + 9) / 5 = [1, 1]. The gradient of the summed solution is `A^-T [1, 1] = [1, 2] / 5 = [0.2, 0.4]`. The diagonal solution sums to `2 / (2 + theta) + 2`, whose slope at zero is `-2 / 4 = -0.5`. Ridge divides 28 by 14 + 14 and gives 1. The compiled solve of [9, 8] returns [2, 3].

## Exercise 1: Change the right-hand side

Holding A fixed changes only the forcing values.

**Expected:** [1,1].

```python
close(jnp.linalg.solve(matrix, jnp.array([4.0, 3.0])), [1.0, 1.0])
```

**Plausible wrong approach:** Computing the gradient as `A^-1 [1, 1]` instead of the transposed solve gives the right numbers here only because A is symmetric. For a nonsymmetric matrix the pullback must use `A.T`, which the residual check confirms.

## Exercise 2: Differentiate with respect to b

The pullback solves the transposed system against an all-ones output cotangent.

**Expected:** [0.2,0.4].

```python
gradient = jax.grad(lambda b: jnp.linalg.solve(matrix, b).sum())(right)
close(gradient, [0.2, 0.4])
close(matrix.T @ gradient, [1.0, 1.0])
```

**Plausible wrong approach:** Relying on `jnp.linalg.solve` to raise for [[1, 2], [2, 4]] does not work: it does not raise a Python error and can return infinite or meaningless entries. Rejection has to come from `admitted_matrix`.

## Exercise 3: Reject a singular fixture

The second row is twice the first, so the system does not define a unique solution for arbitrary b.

**Expected:** ValueError.

```python
try:
    admitted_matrix(jnp.array([[1.0, 2.0], [2.0, 4.0]]))
except ValueError:
    pass
else:
    raise AssertionError("singular matrix admitted")
```

**Plausible wrong approach:** Rejecting matrices by a small determinant depends on scale: multiplying a well-conditioned matrix by 0.001 shrinks the determinant without making the solve any harder. The condition number is scale free.

## Exercise 4: Check the sensitivity numerically

The perturbed matrices remain within the local nonsingular regime.

**Expected:** -0.5 within absolute 1e-8.

```python
h = 1e-5
finite = (parameter_solution(h).sum() - parameter_solution(-h).sum()) / (2 * h)
close(finite, -0.5, atol=1e-8, rtol=0.0)
```

**Plausible wrong approach:** A forward difference at h = 1e-5 has an error near `h / 2` times the second derivative 0.5, about 2.5e-6, which misses the 1e-8 bound. The central difference removes that leading term.

## Exercise 5: Interpret ridge regularization

The denominator changes from 14 to 28 while the cross-product numerator remains 28.

**Expected:** Ridge coefficient one, versus unpenalized two.

```python
x = jnp.array([[1.0], [2.0], [3.0]])
y = 2 * x[:, 0]
ridge = jnp.linalg.solve(x.T @ x + 14 * jnp.eye(1), x.T @ y)
close(ridge, [1.0])
```

**Plausible wrong approach:** Expecting ridge to keep the coefficient 2 because y = 2x fits exactly overlooks that the penalty charges coefficient size, not residual size. Adding 14 to the denominator halves the coefficient.

## Exercise 6: Compile a valid solve

Compilation does not eliminate the need for conditioning and problem-validation checks.

**Expected:** The same [2,3] result with a small residual.

```python
compiled = jax.jit(jnp.linalg.solve)
solution = compiled(matrix, right)
close(solution, [2.0, 3.0])
close(matrix @ solution, right)
```

**Plausible wrong approach:** Treating `jax.jit(jnp.linalg.solve)` as a validated solver mistakes speed for checking. Compilation would solve a nearly singular system just as silently, so the residual and conditioning checks remain.

## How to verify

Run the reference and confirm `jax-019: 8 asserted cases passed`. Compute `np.linalg.cond(np.asarray(matrix))` and note that it is small, then compute it for [[1, 2], [2, 4]] and see an enormous or infinite value. Multiplying `matrix @ jnp.array([1., 1.])` back to [4, 3] confirms the first task by residual.

## Scope of this evidence

A large sensitivity with a small residual can be an ill-conditioned problem rather than a broken solver. A validation threshold is a declared policy, not a theorem. State the assumptions of a differentiable unique solution and test both primal residual and derivative behavior.

Connect the ridge calculation to the statistics book's bias-variance discussion. Design a sensitivity report that separates perturbation of data, regularization choice and floating-point effects instead of calling every difference solver error.
