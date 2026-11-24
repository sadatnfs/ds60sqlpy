# jax-008: explained reference

Let \(f(x)=(x_0^2,x_0x_1,\sin x_1)\). At \(x=(2,0)\), the Jacobian is \(J=\begin{bmatrix}4&0\\0&2\\0&1\end{bmatrix}\). With \(v=(3,4)\), \(Jv=(12,8,4)\). With \(u=(1,2,3)\), \(J^{\mathsf T}u=(4,7)\). Both inner products in the duality relation equal 40. The derivative depends on the evaluation point, not only the function's input shape.

## Solution approach

Fix the point `(2, 0)` and write the 3 by 2 Jacobian of `(a * a, a * b, sin(b))` by hand: rows [4, 0], [0, 2] and [0, 1]. A JVP multiplies that matrix by an input-space direction and returns three numbers. A VJP multiplies its transpose by an output-space cotangent and returns two numbers. Each task chooses a direction or cotangent and predicts the result from the matrix.

**Why it is correct here:** Direction [1, 0] selects the first column [4, 0, 0]. Cotangent [0, 1, 0] selects the second row [0, 2]. With v = [3, 4], Jv = [12, 8, 4] and u . Jv = 12 + 16 + 12 = 40; with u = [1, 2, 3], the pullback is [4, 7] and v . [4, 7] = 12 + 28 = 40. At (1, 1) the rows become [2, 0], [1, 1] and [0, cos 1].

## Exercise 1: Probe the first input coordinate

A coordinate-direction probe selects one column of the derivative map.

**Expected:** [4,0,0], the first Jacobian column.

```python
close(jax.jvp(function, (point,), (jnp.array([1.0, 0.0]),))[1], [4.0, 0.0, 0.0])
```

**Plausible wrong approach:** Expecting the JVP along [1, 0] to return the first row [4, 0] confuses the two products. A JVP output lives in the three-dimensional output space, so it is the first column [4, 0, 0].

## Exercise 2: Probe the second output coordinate

A coordinate cotangent selects one output's sensitivities to all inputs.

**Expected:** [0,2], the second Jacobian row transposed.

```python
_, back = jax.vjp(function, point)
close(back(jnp.array([0.0, 1.0, 0.0]))[0], [0.0, 2.0])
```

**Plausible wrong approach:** Passing the input-shaped vector [0, 1] to `back` is rejected, because the cotangent must match the output shape (3,). The pullback consumes output sensitivities and returns input sensitivities.

## Exercise 3: Check duality

This identity connects the forward and reverse linear maps at one point.

**Expected:** Both 40.

```python
v, u = jnp.array([3.0, 4.0]), jnp.array([1.0, 2.0, 3.0])
jv = jax.jvp(function, (point,), (v,))[1]
_, back = jax.vjp(function, point)
close(jnp.vdot(u, jv), 40.0)
close(jnp.vdot(v, back(u)[0]), 40.0)
```

**Plausible wrong approach:** Comparing `Jv` with `J^T u` directly compares a length-3 vector with a length-2 vector. Duality is a statement about two scalars, `u . Jv` and `v . J^T u`, both 40.

## Exercise 4: Check a directional finite difference

The perturbation changes the input in exactly the direction supplied to JVP.

**Expected:** Agreement with JVP within absolute 1e-8.

```python
direction, h = jnp.array([3.0, 4.0]), 1e-5
finite = (function(point + h * direction) - function(point - h * direction)) / (2 * h)
close(finite, jacobian @ direction, atol=1e-8, rtol=0.0)
```

**Plausible wrong approach:** A one-sided difference along [3, 4] with h = 1e-5 has an error of about `h / 2` times the second directional derivative, 18 for the first output, giving roughly 9e-5. That breaks the 1e-8 bound; the central form passes.

## Exercise 5: Change the point

The bilinear and sinusoidal derivatives change with the evaluation point.

**Expected:** [[2,0],[1,1],[0,cos(1)]].

```python
close(jax.jacfwd(function)(jnp.array([1.0, 1.0])), [[2.0, 0.0], [1.0, 1.0], [0.0, math.cos(1.0)]])
```

**Plausible wrong approach:** Reusing the stored `jacobian` constant at [1, 1] gives the wrong answer, since that matrix was computed for (2, 0). Both the bilinear entries and `cos(b)` change with the point.

## Exercise 6: Recover a scalar gradient

A scalar objective supplies one cotangent; its chain rule is the same pullback.

**Expected:** [4,7], matching the VJP.

```python
weights = jnp.array([1.0, 2.0, 3.0])
close(jax.grad(lambda z: jnp.vdot(weights, function(z)))(point), [4.0, 7.0])
```

**Plausible wrong approach:** Differentiating the unweighted `jnp.sum(function(z))` gives J^T [1, 1, 1] = [4, 3], not [4, 7]. The weights [1, 2, 3] are the cotangent, and dropping them changes the objective.

## How to verify

Run the reference and confirm `jax-008: 8 asserted cases passed`. Then compute `jax.jacfwd(function)(point)` and compare it entry by entry with the hand matrix. Multiply that matrix by [3, 4] and its transpose by [1, 2, 3] with plain NumPy, and confirm you get [12, 8, 4] and [4, 7] independently of the JVP and VJP calls.

## Scope of this evidence

A tangent shape belongs to the input and a cotangent shape belongs to the output. If the result is transposed or has the wrong length, write these spaces down before changing an axis. Agreement between two autodiff calls should still be paired with an independent analytical or directional oracle.

Explain how a scientific simulator with many outputs and few parameters differs from a scalar training objective with many parameters. Choose a derivative question before choosing a mode, then connect the choice to memory and the number of directions actually needed.
