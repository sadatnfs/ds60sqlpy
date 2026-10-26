# jax-007: explained reference

For \(x=[1,2,3]\), \(y=2x\), the mean squared objective is \(L(w)=\frac{14}{3}(w-2)^2\). Thus \(L'(w)=\frac{28}{3}(w-2)\). At zero, the loss is \(56/3\) and the gradient is \(-56/3\). SGD with \(\eta=0.1\) gives \(w'=28/15\), whose fresh loss is \(56/675\). These four numbers are separate observations. A different denominator or broadcast can preserve one while changing the others.

## Exercise 1: Check another smooth point

Moving halfway to the optimum halves the gradient magnitude for this quadratic.

**Expected:** -28/3.

```python
close(jax.grad(loss)(1.), -28 / 3)
```

## Exercise 2: Use a central difference

Both perturbed losses must recompute the full expression from their own weight.

**Expected:** Agreement within absolute 1e-8.

```python
w, h = .7, 1e-5
numerical = (loss(w + h) - loss(w - h)) / (2 * h)
close(numerical, jax.grad(loss)(w), atol=1e-8, rtol=0.)
```

## Exercise 3: Change the reduction

A sum gives each of the three observations its full contribution without dividing by count.

**Expected:** -56, three times the mean-loss gradient.

```python
summed = lambda w: jnp.sum((w * x - y) ** 2)
close(jax.grad(summed)(0.), -56.)
```

## Exercise 4: Inspect the optimum

This exact fixture has an algebraic zero-residual solution; a general fitted model need not.

**Expected:** Both zero.

```python
value, gradient = jax.value_and_grad(loss)(2.)
close(value, 0.)
close(gradient, 0.)
```

## Exercise 5: Differentiate a parameter tree

The bias derivative averages two times each residual, while the weight derivative also multiplies by input.

**Expected:** Weight gradient -56/3; bias gradient -8.

```python
def affine_loss(p):
    return jnp.mean((p['weight'] * x + p['bias'] - y) ** 2)
g = jax.grad(affine_loss)({'weight': jnp.float64(0.), 'bias': jnp.float64(0.)})
close(g['weight'], -56 / 3)
close(g['bias'], -8.)
```

## Exercise 6: Choose a scalar objective

The repair chooses a mathematical objective. It is not merely making an error message disappear.

**Expected:** TypeError for vector output; a finite gradient for its mean.

```python
vector_loss = lambda w: (w * x - y) ** 2
try:
    jax.grad(vector_loss)(0.)
except TypeError:
    pass
else:
    raise AssertionError('vector objective accepted')
close(jax.grad(lambda w: vector_loss(w).mean())(0.), -56 / 3)
```

## Scope of this evidence

For a surprising derivative, inspect reduction, shape, stopped paths and whether the independent finite difference recomputes the full function. For a surprising reported training loss, check whether it came from before or after the update. Increasing tolerance cannot repair a wrong objective.

Compare this exact scalar oracle with torch-008 and tf-008 using matched dtype, inputs and reduction. Explain returned gradients versus mutable gradient buffers. A matching one-step result is a useful porting check, not proof that whole training workflows are equivalent.
