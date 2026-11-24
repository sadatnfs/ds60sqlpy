# jax-021: explained reference

For \(X=\mu+\sigma\epsilon\) with standard normal epsilon, \(\mathbb E[X^2]=\mu^2+\sigma^2\). A fixed sample estimates this by \(\widehat M=N^{-1}\sum_i(\mu+\sigma\epsilon_i)^2\). Its derivatives are \(2N^{-1}\sum_i(\mu+\sigma\epsilon_i)\) and \(2N^{-1}\sum_i(\mu+\sigma\epsilon_i)\epsilon_i\). For the authored symmetric pair and \((\mu,\sigma)=(2,3)\), these give 13, 4 and 6 exactly.

## Solution approach

Expand the objective: the mean of `(m + s * z) ** 2` is `m ** 2 + 2 * m * s * mean(z) + s ** 2 * mean(z ** 2)`. The two-point control [-1, 1] has `mean(z) = 0` and `mean(z ** 2) = 1`, so it reduces to `m ** 2 + s ** 2` exactly. The 1024 normal draws only approximate those moments, so tasks on them check method and replay, not exact values.

**Why it is correct here:** With the control pair, means [0, 1, 2] at scale 3 give 9, 10 and 13. Mean zero and scale two give 4 with zero slope in the mean. Through `s = exp(u)`, the slope in u is `2 * s * s = 18` at s = 3. The objective is quadratic in the mean, so a central difference on fixed noise matches autodiff up to rounding.

## Exercise 1: Reuse draws in a derivative check

Shared base draws prevent random resampling from contaminating the numerical derivative comparison.

**Expected:** Agreement with autodiff within absolute 1e-7.

```python
h = 1e-5
finite = (sample_objective(2.0 + h, 3.0, noise) - sample_objective(2.0 - h, 3.0, noise)) / (2 * h)
close(finite, jax.grad(sample_objective)(2.0, 3.0, noise), atol=1e-7, rtol=0.0)
```

**Plausible wrong approach:** Drawing fresh noise for `2 + h` and for `2 - h` makes the difference quotient measure sampling noise divided by `2 * h`, which is enormous. The same noise array must feed both evaluations.

## Exercise 2: Parameterize a positive scale

The chain rule multiplies the scale derivative six by the current scale three.

**Expected:** Derivative 18.

```python
function = lambda log_scale: sample_objective(2.0, jnp.exp(log_scale), control)
close(jax.grad(function)(math.log(3.0)), 18.0)
```

**Plausible wrong approach:** Differentiating with respect to the log scale but reporting 6 forgets the chain rule. The scale derivative 6 is multiplied by `exp(u) = 3`, giving 18.

## Exercise 3: Check a zero-mean population formula

Symmetry makes the authored sample's first moment zero.

**Expected:** Objective four and mean derivative zero.

```python
close(sample_objective(0.0, 2.0, control), 4.0)
close(jax.grad(sample_objective)(0.0, 2.0, control), 0.0)
```

**Plausible wrong approach:** Expecting `sample_objective(2., 3., noise)` to equal 13 exactly treats the population value as the sample value. Only the authored control pair has moments that reproduce `m ** 2 + s ** 2` exactly.

## Exercise 4: Retain the Monte Carlo count

The usual variance-over-count expression assumes the declared independent sampling design; it is not applied to the two authored control points as a population study.

**Expected:** A finite nonnegative SE with N=1024 explicitly retained.

```python
draws = (2.0 + 3.0 * noise) ** 2
count = draws.size
se = jnp.sqrt(jnp.var(draws, ddof=1) / count)
assert count == 1024
assert bool(jnp.isfinite(se)) and float(se) >= 0.0
```

**Plausible wrong approach:** Computing a standard error from the two control points treats an authored design as a random sample. The variance over count formula belongs to the 1024 independent draws, with that count kept explicit.

## Exercise 5: Vectorize parameter comparisons

Sharing draws defines a controlled comparison of parameter settings.

**Expected:** [9,10,13].

```python
values = jax.vmap(lambda mean: sample_objective(mean, 3.0, control))(jnp.array([0.0, 1.0, 2.0]))
close(values, [9.0, 10.0, 13.0])
```

**Plausible wrong approach:** Mapping both arguments with `jax.vmap` would pair each mean with a single control entry instead of evaluating every mean on both draws. The mean is mapped and the control pair is closed over and shared.

## Exercise 6: Replay the sampled input

The complete random-operation contract supports replay.

**Expected:** Matching draws and estimate in the pinned environment.

```python
again = jax.random.normal(jax.random.key(61), (1024,), dtype=jnp.float64)
close(again, noise)
close(sample_objective(2.0, 3.0, again), sample_objective(2.0, 3.0, noise))
```

**Plausible wrong approach:** Replaying with the same key but a different shape or dtype does not reproduce the draws. The full call, key 61, shape (1024,) and float64, is the replay contract.

## How to verify

Run the reference and confirm `jax-021: 8 asserted cases passed`. Print `noise.mean()` and `(noise ** 2).mean()` and check they are near 0 and 1 but not exact. Then compute `4 + 9 * (noise ** 2).mean() + 12 * noise.mean()` and confirm it equals `sample_objective(2., 3., noise)` to rounding.

## Scope of this evidence

If a finite-difference sensitivity is noisy, first check whether the base draws changed. If a sample estimate differs from its analytic expectation, quantify sampling error before changing the algorithm. Autodiff of a discrete draw requires a separately justified estimator.

Design a comparison of two simulation policies using common random numbers and independent repeated replications. State which uncertainty comes from Monte Carlo sampling and which comes from model or data assumptions.
