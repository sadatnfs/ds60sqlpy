# jax-009: explained reference

For \(f(x)=x_0^2+x_0x_1+2x_1^2\), the gradient is \((2x_0+x_1,x_0+4x_1)\) and \(H=\begin{bmatrix}2&1\\1&4\end{bmatrix}\). At \((1,2)\), the gradient is \((4,9)\). Applying H to \((2,-1)\) gives \((3,-2)\), and the directional curvature \(v^{\mathsf T}Hv\) is 8. The constant Hessian makes this a controlled oracle rather than a claim about every learned objective.

## Solution approach

Differentiate `a * a + a * b + 2 * b * b` by hand first: the gradient is `(2a + b, a + 4b)` and the Hessian is [[2, 1], [1, 4]] everywhere. The tasks then check the first derivative at (1, 2), compare two ways of building the Hessian, form a Hessian-vector product without the matrix, and contrast this constant curvature with the point-dependent curvature of `z ** 4`.

**Why it is correct here:** At (1, 2) the gradient is (2 + 2, 1 + 8) = (4, 9). For v = [2, -1], Hv = (4 - 1, 2 - 4) = (3, -2), and `v . Hv = 6 + 2 = 8`. A degree-two polynomial has a constant Hessian, so (-3, 7) returns the same matrix. For `z ** 4` the second derivative is `12 * z ** 2`, which is 0 at zero and 48 at two.

## Exercise 1: Check the first derivative

A second-order check is difficult to interpret if the first-order objective is wrong.

**Expected:** [4,9].

```python
close(jax.grad(quadratic)(point), [4.0, 9.0])
```

**Plausible wrong approach:** Forgetting that the cross term `a * b` feeds both partial derivatives gives (2, 8) instead of (4, 9). Each coordinate's derivative picks up the other coordinate from that product.

## Exercise 2: Reverse the transform order

The algorithms differ, while the smooth local derivative contract is the same.

**Expected:** Both match the same two-by-two matrix.

```python
close(jax.jacrev(jax.grad(quadratic))(point), expected_hessian)
```

**Plausible wrong approach:** Calling `jax.jacrev(quadratic)(point)` returns the gradient [4, 9] with shape (2,), not the Hessian. The second derivative needs `jacrev` applied to `jax.grad`, which produces the (2, 2) result.

## Exercise 3: Check a matrix-free product numerically

This perturbs the complete gradient calculation in the exact direction under investigation.

**Expected:** [3,-2] within absolute 1e-8.

```python
v, h = jnp.array([2.0, -1.0]), 1e-5
gradient = jax.grad(quadratic)
finite = (gradient(point + h * v) - gradient(point - h * v)) / (2 * h)
close(finite, [3.0, -2.0], atol=1e-8, rtol=0.0)
```

**Plausible wrong approach:** Central-differencing the scalar loss along v gives the directional derivative `grad . v = 8 - 9 = -1`, a single number. The matrix-free product perturbs the gradient function, which returns the vector [3, -2].

## Exercise 4: Interpret directional curvature

The scalar weights a local second-order change along one direction.

**Expected:** 8, a positive curvature in this direction.

```python
v = jnp.array([2.0, -1.0])
close(jnp.vdot(v, expected_hessian @ v), 8.0)
```

**Plausible wrong approach:** Reading the mixed-sign vector Hv = [3, -2] as evidence of negative curvature is a misreading. Curvature along v is the scalar `v . Hv = 8`, which is positive.

## Exercise 5: Change the evaluation point

A degree-two polynomial has a constant second derivative. A nonlinear objective need not.

**Expected:** The same constant Hessian.

```python
close(jax.hessian(quadratic)(jnp.array([-3.0, 7.0])), expected_hessian)
```

**Plausible wrong approach:** Building the evaluation point as `jnp.array([-3, 7])` creates an integer array, and JAX refuses to differentiate integer inputs. The float literals make the Hessian call valid.

## Exercise 6: Contrast nonlinear curvature

Curvature now depends on the point, so one stored Hessian cannot describe every region.

**Expected:** 0 and 48.

```python
second = jax.grad(jax.grad(lambda z: z**4))
close(second(0.0), 0.0)
close(second(2.0), 48.0)
```

**Plausible wrong approach:** Storing the curvature of `z ** 4` measured at zero, which is 0, and reusing it at z = 2 predicts no bending where the true value is 48. Nonquadratic curvature must be recomputed at each point.

## How to verify

Run the reference and confirm `jax-009: 8 asserted cases passed`. Print `jax.hessian(quadratic)(point)` and compare it with [[2, 1], [1, 4]]. Then compute `jax.jvp(jax.grad(quadratic), (point,), (v,))[1]` as a second matrix-free route and expect [3, -2], matching both the finite difference and `expected_hessian @ v`.

## Scope of this evidence

A dense Hessian's successful construction can conceal an unnecessary memory cost. Check whether the task needs the full matrix, a diagonal approximation or products with selected vectors. Do not interpret finite-difference failure at a nonsmooth point as proof that all autodiff is broken.

Connect curvature to the least-squares Hessian in the statistics book. Explain when a matrix-free product would be sufficient for an iterative method, and which additional convergence and conditioning assumptions that method would need.
