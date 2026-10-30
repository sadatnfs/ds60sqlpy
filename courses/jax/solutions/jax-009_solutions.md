# jax-009: explained reference

For \(f(x)=x_0^2+x_0x_1+2x_1^2\), the gradient is \((2x_0+x_1,x_0+4x_1)\) and \(H=\begin{bmatrix}2&1\\1&4\end{bmatrix}\). At \((1,2)\), the gradient is \((4,9)\). Applying H to \((2,-1)\) gives \((3,-2)\), and the directional curvature \(v^{\mathsf T}Hv\) is 8. The constant Hessian makes this a controlled oracle rather than a claim about every learned objective.

## Exercise 1: Check the first derivative

A second-order check is difficult to interpret if the first-order objective is wrong.

**Expected:** [4,9].

```python
close(jax.grad(quadratic)(point), [4.0, 9.0])
```

## Exercise 2: Reverse the transform order

The algorithms differ, while the smooth local derivative contract is the same.

**Expected:** Both match the same two-by-two matrix.

```python
close(jax.jacrev(jax.grad(quadratic))(point), expected_hessian)
```

## Exercise 3: Check a matrix-free product numerically

This perturbs the complete gradient calculation in the exact direction under investigation.

**Expected:** [3,-2] within absolute 1e-8.

```python
v, h = jnp.array([2.0, -1.0]), 1e-5
gradient = jax.grad(quadratic)
finite = (gradient(point + h * v) - gradient(point - h * v)) / (2 * h)
close(finite, [3.0, -2.0], atol=1e-8, rtol=0.0)
```

## Exercise 4: Interpret directional curvature

The scalar weights a local second-order change along one direction.

**Expected:** 8, a positive curvature in this direction.

```python
v = jnp.array([2.0, -1.0])
close(jnp.vdot(v, expected_hessian @ v), 8.0)
```

## Exercise 5: Change the evaluation point

A degree-two polynomial has a constant second derivative. A nonlinear objective need not.

**Expected:** The same constant Hessian.

```python
close(jax.hessian(quadratic)(jnp.array([-3.0, 7.0])), expected_hessian)
```

## Exercise 6: Contrast nonlinear curvature

Curvature now depends on the point, so one stored Hessian cannot describe every region.

**Expected:** 0 and 48.

```python
second = jax.grad(jax.grad(lambda z: z**4))
close(second(0.0), 0.0)
close(second(2.0), 48.0)
```

## Scope of this evidence

A dense Hessian's successful construction can conceal an unnecessary memory cost. Check whether the task needs the full matrix, a diagonal approximation or products with selected vectors. Do not interpret finite-difference failure at a nonsmooth point as proof that all autodiff is broken.

Connect curvature to the least-squares Hessian in the statistics book. Explain when a matrix-free product would be sufficient for an iterative method, and which additional convergence and conditioning assumptions that method would need.
