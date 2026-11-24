# jax-022: explained reference

Stable softplus is \(s(x)=\log(1+e^x)\), with derivative \(\sigma(x)\). Its JVP maps tangent t to \(\sigma(x)t\), which is linear in t. For \(f(x)=x^2\), a VJP maps output cotangent u to \(2xu\). At x=3 and u=4, the pullback is 24. Returning only 2x would pass a unit-upstream case and fail this composition.

## Solution approach

Test a custom rule against something it did not define. Softplus has the known derivative `sigmoid(x)` and second derivative `sigmoid(x) * (1 - sigmoid(x))`. The custom square has the known derivative `2 * x`. Each task checks the rule against these independent formulas, against linearity in the tangent, at an extreme input, and at the boundary of what `custom_vjp` provides.

**Why it is correct here:** At -2, 0 and 2 the gradient equals `jax.nn.sigmoid` of the same points. The rule multiplies the tangent by `sigmoid(1)`, so tangents 2 and 3 sum to tangent 5. At 1000 `logaddexp(0, 1000)` is 1000 and sigmoid is 1. Four times the square has slope `4 * 2 * 3 = 24`. At zero, `sigmoid(0) * (1 - sigmoid(0)) = 0.25`.

## Exercise 1: Compare an ordinary gradient

The independent primitive provides a direct analytic derivative implementation.

**Expected:** Matching values.

```python
points = jnp.array([-2.0, 0.0, 2.0])
close(jax.vmap(jax.grad(stable_softplus))(points), jax.nn.sigmoid(points))
```

**Plausible wrong approach:** Writing softplus as `jnp.log(1 + jnp.exp(x))` overflows `exp(1000)` to infinity, so the value is infinite. `logaddexp` evaluates the same function without forming the huge exponential.

## Exercise 2: Check tangent linearity

Linearity is required of the local derivative map, not an optional optimization.

**Expected:** The five-direction result equals the sum of the two and three results.

```python
jvp = lambda tangent: jax.jvp(stable_softplus, (jnp.float64(1.0),), (jnp.float64(tangent),))[1]
close(jvp(5.0), jvp(2.0) + jvp(3.0))
```

**Plausible wrong approach:** Returning `sigmoid(value)` as the tangent output without multiplying by `tangent` makes the JVP ignore its direction. Tangents 2, 3 and 5 would all give the same number, and linearity fails.

## Exercise 3: Check an extreme stable input

The primal avoids constructing exp(1000); the derivative also remains representable.

**Expected:** Finite value 1000 and gradient one.

```python
close(stable_softplus(1000.0), 1000.0)
close(jax.grad(stable_softplus)(1000.0), 1.0)
```

**Plausible wrong approach:** Having `square_backward` return `2 * saved` and ignore the cotangent passes a plain gradient check but breaks composition: the derivative of `4 * x * x` would come out as 6 instead of 24.

## Exercise 4: Differentiate a composition

This independently tests that upstream scaling survives through grad.

**Expected:** 24.

```python
close(jax.grad(lambda x: 4 * custom_square(x))(3.0), 24.0)
```

**Plausible wrong approach:** Testing the custom gradient only at zero, where `sigmoid` is 0.5, would also accept a rule that always returns 0.5. The three points -2, 0 and 2 separate the correct rule from constant mistakes.

## Exercise 5: Check a second derivative

This exercises a higher derivative of the implemented custom rule rather than assuming it from the first derivative.

**Expected:** 0.25.

```python
close(jax.grad(jax.grad(stable_softplus))(0.0), 0.25)
```

**Plausible wrong approach:** Expecting the second derivative to fail or be zero assumes a custom JVP blocks further differentiation. JAX differentiates the rule itself, and `sigmoid` is smooth, so the answer is 0.25.

## Exercise 6: Name the forward-mode limit

The VJP decorator provides reverse-mode behavior, not an automatic forward-mode rule.

**Expected:** TypeError under the documented custom_vjp contract.

```python
try:
    jax.jvp(custom_square, (jnp.float64(3.0),), (jnp.float64(1.0),))
except TypeError:
    pass
else:
    raise AssertionError("unexpected custom_vjp forward-mode support")
```

**Plausible wrong approach:** Assuming `jax.jvp` works through `custom_square` because the function is a plain product overlooks the decorator. `custom_vjp` supplies only reverse mode, so the forward call raises TypeError.

## How to verify

Once `jax-022: 8 asserted cases passed` appears, check `jax.grad(stable_softplus)(1.)` against `1 / (1 + math.exp(-1))` from the standard library. Then temporarily drop the cotangent factor in a copy of `square_backward` and watch the composition task fail with 6 instead of 24.

## Scope of this evidence

A correct forward result cannot validate a custom backward rule. Include non-unit upstream values, tangent linearity, independent derivatives and the transformation compositions you intend to support. Keep unsupported modes explicit rather than silently detaching a computation.

Propose a custom derivative for an implicit scientific computation and list its required residuals. Explain which assumptions would justify it and how you would detect a rule that returns a plausible but incorrect gradient.
