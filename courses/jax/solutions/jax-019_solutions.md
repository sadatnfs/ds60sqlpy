# jax-019: explained reference

Differentiating \(A(\theta)x(\theta)=b(\theta)\) gives \(A\,dx/db=I\) when only b varies, and \(dx/d\theta=A^{-1}(db/d\theta-(dA/d\theta)x)\). This identity describes a solve, not a recommendation to form an inverse. For \(A=\operatorname{diag}(2+\theta,3)\), \(b=(2,6)\), the solution is \((2/(2+\theta),2)\). At zero, the derivative of its summed coordinates is \(-1/2\).

## Exercise 1: Change the right-hand side

Holding A fixed changes only the forcing values.

**Expected:** [1,1].

```python
close(jnp.linalg.solve(matrix, jnp.array([4., 3.])), [1., 1.])
```

## Exercise 2: Differentiate with respect to b

The pullback solves the transposed system against an all-ones output cotangent.

**Expected:** [0.2,0.4].

```python
gradient = jax.grad(lambda b: jnp.linalg.solve(matrix, b).sum())(right)
close(gradient, [.2, .4])
close(matrix.T @ gradient, [1., 1.])
```

## Exercise 3: Reject a singular fixture

The second row is twice the first, so the system does not define a unique solution for arbitrary b.

**Expected:** ValueError.

```python
try:
    admitted_matrix(jnp.array([[1., 2.], [2., 4.]]))
except ValueError:
    pass
else:
    raise AssertionError('singular matrix admitted')
```

## Exercise 4: Check the sensitivity numerically

The perturbed matrices remain within the local nonsingular regime.

**Expected:** -0.5 within absolute 1e-8.

```python
h = 1e-5
finite = (parameter_solution(h).sum() - parameter_solution(-h).sum()) / (2 * h)
close(finite, -.5, atol=1e-8, rtol=0.)
```

## Exercise 5: Interpret ridge regularization

The denominator changes from 14 to 28 while the cross-product numerator remains 28.

**Expected:** Ridge coefficient one, versus unpenalized two.

```python
x = jnp.array([[1.], [2.], [3.]])
y = 2 * x[:, 0]
ridge = jnp.linalg.solve(x.T @ x + 14 * jnp.eye(1), x.T @ y)
close(ridge, [1.])
```

## Exercise 6: Compile a valid solve

Compilation does not eliminate the need for conditioning and problem-admission checks.

**Expected:** The same [2,3] result with a small residual.

```python
compiled = jax.jit(jnp.linalg.solve)
solution = compiled(matrix, right)
close(solution, [2., 3.])
close(matrix @ solution, right)
```

## Scope of this evidence

A large sensitivity with a small residual can be an ill-conditioned problem rather than a broken solver. An admission threshold is a declared policy, not a theorem. State the assumptions of a differentiable unique solution and test both primal residual and derivative behavior.

Connect the ridge calculation to the statistics book's bias-variance discussion. Design a sensitivity report that separates perturbation of data, regularization choice and floating-point effects instead of calling every difference solver error.
