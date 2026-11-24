# jax-007: explained reference

For \(x=[1,2,3]\), \(y=2x\), the mean squared objective is \(L(w)=\frac{14}{3}(w-2)^2\). Thus \(L'(w)=\frac{28}{3}(w-2)\). At zero, the loss is \(56/3\) and the gradient is \(-56/3\). SGD with \(\eta=0.1\) gives \(w'=28/15\), whose fresh loss is \(56/675\). These four numbers are separate observations. A different denominator or broadcast can preserve one while changing the others.

## Solution approach

Write the loss in closed form before calling `jax.grad`. With `x = [1, 2, 3]` and `y = 2 * x`, the residual is `(w - 2) * x`, so `L(w) = 14 * (w - 2) ** 2 / 3` and `L'(w) = 28 * (w - 2) / 3`. Every task compares autodiff with this formula, with a central difference, or with a hand derivative for an extra parameter.

**Why it is correct here:** At w = 1 the formula gives -28/3, and at w = 2 both value and slope are zero. Summing instead of averaging multiplies the gradient by three, giving -56 at zero. For the affine model at zero, the residuals are -y = [-2, -4, -6]; the bias derivative is `2 * mean(-y) = -8` and the weight derivative is `2 * mean(-y * x) = -56/3`.

## Exercise 1: Check another smooth point

Moving halfway to the optimum halves the gradient magnitude for this quadratic.

**Expected:** -28/3.

```python
close(jax.grad(loss)(1.0), -28 / 3)
```

**Plausible wrong approach:** Dropping the factor 2 from the derivative of the square gives -14/3 at weight one. Autodiff applies the full chain rule, so the hand formula must keep `2 * (w * x - y) * x`.

## Exercise 2: Use a central difference

Both perturbed losses must recompute the full expression from their own weight.

**Expected:** Agreement within absolute 1e-8.

```python
w, h = 0.7, 1e-5
numerical = (loss(w + h) - loss(w - h)) / (2 * h)
close(numerical, jax.grad(loss)(w), atol=1e-8, rtol=0.0)
```

**Plausible wrong approach:** A forward difference `(loss(w + h) - loss(w)) / h` carries an error near `h * L'' / 2`, about 4.7e-5 for `L'' = 28/3`, which fails the 1e-8 bound. The central difference cancels that term for this quadratic.

## Exercise 3: Change the reduction

A sum gives each of the three observations its full contribution without dividing by count.

**Expected:** -56, three times the mean-loss gradient.

```python
summed = lambda w: jnp.sum((w * x - y) ** 2)
close(jax.grad(summed)(0.0), -56.0)
```

**Plausible wrong approach:** Expecting the summed loss to share the mean loss gradient of -56/3 ignores the missing division by three. The two objectives have the same minimizer but different slopes.

## Exercise 4: Inspect the optimum

This exact fixture has an algebraic zero-residual solution; a general fitted model need not.

**Expected:** Both zero.

```python
value, gradient = jax.value_and_grad(loss)(2.0)
close(value, 0.0)
close(gradient, 0.0)
```

**Plausible wrong approach:** Locating the optimum by noticing that `loss(1.5)` and `loss(2.5)` both equal 7/6 suggests symmetry around 2 but does not show a zero slope. `value_and_grad` at 2.0 checks the value and the derivative directly.

## Exercise 5: Differentiate a parameter tree

The bias derivative averages two times each residual, while the weight derivative also multiplies by input.

**Expected:** Weight gradient -56/3; bias gradient -8.

```python
def affine_loss(p):
    return jnp.mean((p["weight"] * x + p["bias"] - y) ** 2)


g = jax.grad(affine_loss)({"weight": jnp.float64(0.0), "bias": jnp.float64(0.0)})
close(g["weight"], -56 / 3)
close(g["bias"], -8.0)
```

**Plausible wrong approach:** Leaving out the factor 2 for the bias gives -4, the plain mean residual. The bias enters every prediction with coefficient one, so its derivative is twice the mean residual, -8.

## Exercise 6: Choose a scalar objective

The repair chooses a mathematical objective. It is not merely making an error message disappear.

**Expected:** TypeError for vector output; a finite gradient for its mean.

```python
vector_loss = lambda w: (w * x - y) ** 2
try:
    jax.grad(vector_loss)(0.0)
except TypeError:
    pass
else:
    raise AssertionError("vector objective accepted")
close(jax.grad(lambda w: vector_loss(w).mean())(0.0), -56 / 3)
```

**Plausible wrong approach:** Swapping `jax.grad` for `jax.jacobian` makes the error disappear but returns three per-observation slopes [-4, -16, -36]. No objective was chosen; the mean of that vector, -56/3, is the gradient of the mean loss.

## How to verify

Run the reference and confirm `jax-007: 8 asserted cases passed`. Then evaluate `28 * (w - 2) / 3` at w = 0, 0.7 and 1 by hand and compare with `jax.grad(loss)`. Apply one SGD step with rate 0.1 from zero to reach 28/15, and check that `loss(28 / 15)` equals 56/675, which ties the gradient to a decrease in the loss.

## Scope of this evidence

For a surprising derivative, inspect reduction, shape, stopped paths and whether the independent finite difference recomputes the full function. For a surprising reported training loss, check whether it came from before or after the update. Increasing tolerance cannot repair a wrong objective.

Compare this exact scalar oracle with torch-008 and tf-008 using matched dtype, inputs and reduction. Explain returned gradients versus mutable gradient buffers. A matching one-step result is a useful porting check, not proof that whole training workflows are equivalent.
