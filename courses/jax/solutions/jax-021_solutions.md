# jax-021: explained reference

For \(X=\mu+\sigma\epsilon\) with standard normal epsilon, \(\mathbb E[X^2]=\mu^2+\sigma^2\). A fixed sample estimates this by \(\widehat M=N^{-1}\sum_i(\mu+\sigma\epsilon_i)^2\). Its derivatives are \(2N^{-1}\sum_i(\mu+\sigma\epsilon_i)\) and \(2N^{-1}\sum_i(\mu+\sigma\epsilon_i)\epsilon_i\). For the authored symmetric pair and \((\mu,\sigma)=(2,3)\), these give 13, 4 and 6 exactly.

## Exercise 1: Reuse draws in a derivative check

Shared base draws prevent random resampling from contaminating the numerical derivative comparison.

**Expected:** Agreement with autodiff within absolute 1e-7.

```python
h = 1e-5
finite = (sample_objective(2. + h, 3., noise) - sample_objective(2. - h, 3., noise)) / (2 * h)
close(finite, jax.grad(sample_objective)(2., 3., noise), atol=1e-7, rtol=0.)
```

## Exercise 2: Parameterize a positive scale

The chain rule multiplies the scale derivative six by the current scale three.

**Expected:** Derivative 18.

```python
function = lambda log_scale: sample_objective(2., jnp.exp(log_scale), control)
close(jax.grad(function)(math.log(3.)), 18.)
```

## Exercise 3: Check a zero-mean population formula

Symmetry makes the authored sample's first moment zero.

**Expected:** Objective four and mean derivative zero.

```python
close(sample_objective(0., 2., control), 4.)
close(jax.grad(sample_objective)(0., 2., control), 0.)
```

## Exercise 4: Retain the Monte Carlo count

The usual variance-over-count expression assumes the declared independent sampling design; it is not applied to the two authored control points as a population study.

**Expected:** A finite nonnegative SE with N=1024 explicitly retained.

```python
draws = (2. + 3. * noise) ** 2
count = draws.size
se = jnp.sqrt(jnp.var(draws, ddof=1) / count)
assert count == 1024
assert bool(jnp.isfinite(se)) and float(se) >= 0.
```

## Exercise 5: Vectorize parameter comparisons

Sharing draws defines a controlled comparison of parameter settings.

**Expected:** [9,10,13].

```python
values = jax.vmap(lambda mean: sample_objective(mean, 3., control))(jnp.array([0., 1., 2.]))
close(values, [9., 10., 13.])
```

## Exercise 6: Replay the sampled input

The complete random-operation contract supports replay.

**Expected:** Matching draws and estimate in the pinned environment.

```python
again = jax.random.normal(jax.random.key(61), (1024,), dtype=jnp.float64)
close(again, noise)
close(sample_objective(2., 3., again), sample_objective(2., 3., noise))
```

## Scope of this evidence

If a finite-difference sensitivity is noisy, first check whether the base draws changed. If a sample estimate differs from its analytic expectation, quantify sampling error before changing the algorithm. Autodiff of a discrete draw requires a separately justified estimator.

Design a comparison of two simulation policies using common random numbers and independent repeated replications. State which uncertainty comes from Monte Carlo sampling and which comes from model or data assumptions.
