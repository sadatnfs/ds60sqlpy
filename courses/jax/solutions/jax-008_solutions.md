# jax-008: explained reference

Let \(f(x)=(x_0^2,x_0x_1,\sin x_1)\). At \(x=(2,0)\), the Jacobian is \(J=\begin{bmatrix}4&0\\0&2\\0&1\end{bmatrix}\). With \(v=(3,4)\), \(Jv=(12,8,4)\). With \(u=(1,2,3)\), \(J^{\mathsf T}u=(4,7)\). Both inner products in the duality relation equal 40. The derivative depends on the evaluation point, not only the function's input shape.

## Exercise 1: Probe the first input coordinate

A coordinate-direction probe selects one column of the derivative map.

**Expected:** [4,0,0], the first Jacobian column.

```python
close(jax.jvp(function, (point,), (jnp.array([1., 0.]),))[1], [4., 0., 0.])
```

## Exercise 2: Probe the second output coordinate

A coordinate cotangent selects one output's sensitivities to all inputs.

**Expected:** [0,2], the second Jacobian row transposed.

```python
_, back = jax.vjp(function, point)
close(back(jnp.array([0., 1., 0.]))[0], [0., 2.])
```

## Exercise 3: Check duality

This identity connects the forward and reverse linear maps at one point.

**Expected:** Both 40.

```python
v, u = jnp.array([3., 4.]), jnp.array([1., 2., 3.])
jv = jax.jvp(function, (point,), (v,))[1]
_, back = jax.vjp(function, point)
close(jnp.vdot(u, jv), 40.)
close(jnp.vdot(v, back(u)[0]), 40.)
```

## Exercise 4: Check a directional finite difference

The perturbation changes the input in exactly the direction supplied to JVP.

**Expected:** Agreement with JVP within absolute 1e-8.

```python
direction, h = jnp.array([3., 4.]), 1e-5
finite = (function(point + h * direction) - function(point - h * direction)) / (2 * h)
close(finite, jacobian @ direction, atol=1e-8, rtol=0.)
```

## Exercise 5: Change the point

The bilinear and sinusoidal derivatives change with the evaluation point.

**Expected:** [[2,0],[1,1],[0,cos(1)]].

```python
close(jax.jacfwd(function)(jnp.array([1., 1.])), [[2., 0.], [1., 1.], [0., math.cos(1.)]])
```

## Exercise 6: Recover a scalar gradient

A scalar objective supplies one cotangent; its chain rule is the same pullback.

**Expected:** [4,7], matching the VJP.

```python
weights = jnp.array([1., 2., 3.])
close(jax.grad(lambda z: jnp.vdot(weights, function(z)))(point), [4., 7.])
```

## Scope of this evidence

A tangent shape belongs to the input and a cotangent shape belongs to the output. If the result is transposed or has the wrong length, write these spaces down before changing an axis. Agreement between two autodiff calls should still be paired with an independent analytical or directional oracle.

Explain how a scientific simulator with many outputs and few parameters differs from a scalar training objective with many parameters. Choose a derivative question before choosing a mode, then connect the choice to memory and the number of directions actually needed.
