# jax-023: explained reference

For \(D(\theta)=\operatorname{diag}(2+\theta,3)\), \(x=D^{-1}b\). At \(\theta=0\), b=(2,6), x=(1,2). Holding b fixed gives \(dx/d\theta=(-1/2,0)\). The summed-output pullback with respect to b is \((1/2,1/3)\). Because this diagonal matrix is symmetric, primal and transpose solve equations use the same diagonal entries.

## Solution approach

Write the diagonal system's solution in closed form: x = [2 / (2 + theta), 6 / 3] = [2 / (2 + theta), 2] for the right side [2, 6]. `custom_linear_solve` differentiates by solving another linear system with the supplied solver, so every derivative here is also a division by the diagonal. The tasks check that rule, compare implementations, and expose what happens when the solver lies.

**Why it is correct here:** The pullback of a ones cotangent divides by the diagonal: [1 / 2, 1 / 3]. At theta 2 the first entry is 2 / 4 = 0.5 and the second stays 2. At theta 0.5 both solvers divide [2, 6] by [2.5, 3]. The second derivative of `2 / (2 + theta)` is `4 / (2 + theta) ** 3`, which is 0.5 at zero. At theta 1 the solution is [2 / 3, 2] and multiplying by [3, 3] returns [2, 6].

## Exercise 1: Pull back to the right-hand side

The output cotangent of ones is solved through the transposed diagonal system.

**Expected:** [0.5,1/3].

```python
close(jax.grad(lambda b: implicit_solution(0.0, b).sum())(right), [0.5, 1 / 3])
```

**Plausible wrong approach:** Answering with the solution [1, 2] mixes up the solved vector with its sensitivity. The derivative with respect to the right side is the inverse diagonal applied to ones, [1 / 2, 1 / 3].

## Exercise 2: Change the diagonal

Only the first diagonal entry changes, so only the first solved coordinate changes.

**Expected:** [0.5,2].

```python
close(implicit_solution(2.0, right), [0.5, 2.0])
```

**Plausible wrong approach:** Expecting both coordinates to move when theta changes ignores the structure: theta only enters the first diagonal entry, so the second coordinate stays 6 / 3 = 2.

## Exercise 3: Compare an ordinary solve

The ordinary solver is a second implementation of the same tiny equation, not proof of arbitrary custom-solver convergence.

**Expected:** Matching primal values.

```python
a = jnp.diag(jnp.array([2.5, 3.0]))
close(implicit_solution(0.5, right), jnp.linalg.solve(a, right))
```

**Plausible wrong approach:** Treating agreement with `jnp.linalg.solve` at theta 0.5 as proof that any custom solver converges overreaches. It shows two implementations agree on one tiny, exactly solvable system.

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

**Plausible wrong approach:** Accepting the zero-returning solver because its output is finite skips the only check that matters. Its residual is the whole right side [2, 6], and its derivatives would be wrong as well.

## Exercise 5: Check a second derivative

For 2/(2+theta), the second derivative is 4/(2+theta)^3.

**Expected:** 0.5.

```python
second = jax.grad(jax.grad(lambda theta: implicit_solution(theta, right).sum()))
close(second(0.0), 0.5)
```

**Plausible wrong approach:** Declaring `symmetric=True` for a nonsymmetric operator makes JAX reuse the forward solver for the transposed system and return wrong gradients silently. It is valid here only because a diagonal matrix is symmetric.

## Exercise 6: Compile the valid interface

Compilation compatibility and solver correctness remain separate checks.

**Expected:** [2/3,2], satisfying the diagonal equation.

```python
solution = jax.jit(implicit_solution)(1.0, right)
close(solution, [2 / 3, 2.0])
close(jnp.array([3.0, 3.0]) * solution, right)
```

**Plausible wrong approach:** Dropping the exponent factor when differentiating `-2 / (2 + theta) ** 2` gives `2 / 8 = 0.25`. The power rule brings down the 2, so the second derivative is `4 / 8 = 0.5`.

## How to verify

Run the reference and confirm `jax-023: 8 asserted cases passed`. Evaluate `2 / (2 + t)` and its two derivatives by hand at t = 0 and t = 1 and compare them with `implicit_solution`, `jax.grad` and the nested grad. Then print the residual `diagonal * wrong - right` for the bogus solver and see [-2, -6].

## Scope of this evidence

Do not declare symmetry or convergence to make an API path convenient. Check the primal residual, required transpose behavior and independent sensitivities. Near singularity, the differentiable-solution assumptions and numerical conditioning can fail together.

Describe how you would replace the direct diagonal solver with an iterative matrix-free solver. Specify stopping tolerance, residual evidence, transpose solve and a study of how solve error affects gradient error.
