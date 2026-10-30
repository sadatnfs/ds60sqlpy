# jax-023: explained reference

For \(D(\theta)=\operatorname{diag}(2+\theta,3)\), \(x=D^{-1}b\). At \(\theta=0\), b=(2,6), x=(1,2). Holding b fixed gives \(dx/d\theta=(-1/2,0)\). The summed-output pullback with respect to b is \((1/2,1/3)\). Because this diagonal matrix is symmetric, primal and transpose solve equations use the same diagonal entries.

## Exercise 1: Pull back to the right-hand side

The output cotangent of ones is solved through the transposed diagonal system.

**Expected:** [0.5,1/3].

```python
close(jax.grad(lambda b: implicit_solution(0.0, b).sum())(right), [0.5, 1 / 3])
```

## Exercise 2: Change the diagonal

Only the first diagonal entry changes, so only the first solved coordinate changes.

**Expected:** [0.5,2].

```python
close(implicit_solution(2.0, right), [0.5, 2.0])
```

## Exercise 3: Compare an ordinary solve

The ordinary solver is a second implementation of the same tiny equation, not proof of arbitrary custom-solver convergence.

**Expected:** Matching primal values.

```python
a = jnp.diag(jnp.array([2.5, 3.0]))
close(implicit_solution(0.5, right), jnp.linalg.solve(a, right))
```

## Exercise 4: Detect a bogus solver

custom_linear_solve relies on the supplied solver's correctness and does not establish this invariant automatically.

**Expected:** Finite zero output, but a nonzero residual; the contract fails.

```python
diagonal = jnp.array([2.0, 3.0])
wrong = jax.lax.custom_linear_solve(
    lambda x: diagonal * x, right, solve=lambda operation, rhs: jnp.zeros_like(rhs), symmetric=True
)
assert bool(jnp.isfinite(wrong).all())
assert not np.allclose(np.asarray(diagonal * wrong), np.asarray(right))
```

## Exercise 5: Check a second derivative

For 2/(2+theta), the second derivative is 4/(2+theta)^3.

**Expected:** 0.5.

```python
second = jax.grad(jax.grad(lambda theta: implicit_solution(theta, right).sum()))
close(second(0.0), 0.5)
```

## Exercise 6: Compile the valid interface

Compilation compatibility and solver correctness remain separate checks.

**Expected:** [2/3,2], satisfying the diagonal equation.

```python
solution = jax.jit(implicit_solution)(1.0, right)
close(solution, [2 / 3, 2.0])
close(jnp.array([3.0, 3.0]) * solution, right)
```

## Scope of this evidence

Do not declare symmetry or convergence to make an API path convenient. Check the primal residual, required transpose behavior and independent sensitivities. Near singularity, the differentiable-solution assumptions and numerical conditioning can fail together.

Describe how you would replace the direct diagonal solver with an iterative matrix-free solver. Specify stopping tolerance, residual evidence, transpose solve and a study of how solve error affects gradient error.
