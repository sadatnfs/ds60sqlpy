# jax-022: explained reference

Stable softplus is \(s(x)=\log(1+e^x)\), with derivative \(\sigma(x)\). Its JVP maps tangent t to \(\sigma(x)t\), which is linear in t. For \(f(x)=x^2\), a VJP maps output cotangent u to \(2xu\). At x=3 and u=4, the pullback is 24. Returning only 2x would pass a unit-upstream case and fail this composition.

## Exercise 1: Compare an ordinary gradient

The independent primitive provides a direct analytic derivative implementation.

**Expected:** Matching values.

```python
points = jnp.array([-2., 0., 2.])
close(jax.vmap(jax.grad(stable_softplus))(points), jax.nn.sigmoid(points))
```

## Exercise 2: Check tangent linearity

Linearity is required of the local derivative map, not an optional optimization.

**Expected:** The five-direction result equals the sum of the two and three results.

```python
jvp = lambda tangent: jax.jvp(stable_softplus, (jnp.float64(1.),), (jnp.float64(tangent),))[1]
close(jvp(5.), jvp(2.) + jvp(3.))
```

## Exercise 3: Check an extreme stable input

The primal avoids constructing exp(1000); the derivative also remains representable.

**Expected:** Finite value 1000 and gradient one.

```python
close(stable_softplus(1000.), 1000.)
close(jax.grad(stable_softplus)(1000.), 1.)
```

## Exercise 4: Differentiate a composition

This independently tests that upstream scaling survives through grad.

**Expected:** 24.

```python
close(jax.grad(lambda x: 4 * custom_square(x))(3.), 24.)
```

## Exercise 5: Check a second derivative

This exercises a higher derivative of the implemented custom rule rather than assuming it from the first derivative.

**Expected:** 0.25.

```python
close(jax.grad(jax.grad(stable_softplus))(0.), .25)
```

## Exercise 6: Name the forward-mode limit

The VJP decorator provides reverse-mode behavior, not an automatic forward-mode rule.

**Expected:** TypeError under the documented custom_vjp contract.

```python
try:
    jax.jvp(custom_square, (jnp.float64(3.),), (jnp.float64(1.),))
except TypeError:
    pass
else:
    raise AssertionError('unexpected custom_vjp forward-mode support')
```

## Scope of this evidence

A correct forward result cannot validate a custom backward rule. Include non-unit upstream values, tangent linearity, independent derivatives and the transformation compositions you intend to support. Keep unsupported modes explicit rather than silently detaching a computation.

Propose a custom derivative for an implicit scientific computation and list its required residuals. Explain which assumptions would justify it and how you would detect a rule that returns a plausible but incorrect gradient.
