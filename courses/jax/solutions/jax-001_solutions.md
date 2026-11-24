# jax-001: explained reference

For inputs \(x_i\), targets \(y_i\) and scalar weight \(w\), define \(\widehat y_i=wx_i\) and \(L(w)=N^{-1}\sum_i(\widehat y_i-y_i)^2\). The denominator counts observations because each observation has one output here. With several output coordinates, a mean over every array entry would answer a different weighting question. At \(w=0\), the three residual squares sum to 56 and the loss is \(56/3\). At \(w=2\), every residual is zero. Neither calculation uses a gradient or updates a parameter.

## Solution approach

Every exercise reuses two small functions. `predict` multiplies the scalar weight by the input vector `x = [1, 2, 3]`, and `mse` validates that inputs and targets are nonempty vectors of equal shape before averaging the squared residuals. Work each task by hand first: write the predictions, subtract the targets, square, sum, and divide by three. Only then compare the hand value with the JAX result.

**Why it is correct here:** The targets are exactly `2 * x`, so the residual at weight `w` is `(w - 2) * x`. The loss is therefore `(w - 2) ** 2 * (1 + 4 + 9) / 3 = 14 * (w - 2) ** 2 / 3`. That closed form gives 56/3 at weight 0, 14/3 at weight 1 and 0 at weight 2, which is why the asserted values are exact rather than approximate.

## Exercise 1: Trace another predictor

Each error equals minus the corresponding input; square and average.

**Expected:** [1,2,3] and 14/3.

```python
close(predict(1.0, x), [1.0, 2.0, 3.0])
close(mse(1.0, x, y), 14 / 3)
```

**Plausible wrong approach:** Computing `mse(1., x, y)` as the mean of the errors instead of the squared errors gives -2 rather than 14/3, because the residuals [-1, -2, -3] are all negative and never cancel into a squared quantity.

## Exercise 2: Construct an exact fit

All targets follow the same declared rule, so this is an algebraic fit to the fixture.

**Expected:** Weight 2 gives zero loss.

```python
close(mse(2.0, x, y), 0.0)
```

**Plausible wrong approach:** Searching for the weight with a gradient step is unnecessary and hides the point: dividing any target by its input gives 2 for every observation, so the fit is algebraic and a single `mse(2., x, y)` call proves it.

## Exercise 3: Change the target

Only the final target differs by one; the denominator remains three.

**Expected:** Loss 1/3.

```python
close(mse(2.0, x, jnp.array([2.0, 4.0, 7.0])), 1 / 3)
```

**Plausible wrong approach:** Dividing the single squared residual of 1 by the count of changed targets, one, reports a loss of 1. The mean still runs over all three observations, so the correct value is 1/3.

## Exercise 4: Reject missing observations

An empty mean does not describe a prediction experiment under this contract.

**Expected:** ValueError, not a NaN mean.

```python
try:
    mse(0.0, jnp.array([]), jnp.array([]))
except ValueError:
    pass
else:
    raise AssertionError("empty loss accepted")
```

**Plausible wrong approach:** Letting `jnp.mean` run on two empty arrays returns NaN with a runtime warning, which looks like a number in logs. The guard `inputs.size == 0` raises ValueError before any reduction runs.

## Exercise 5: Separate sum from mean

The equality relies on exactly three equally weighted output entries.

**Expected:** Both are 56.

```python
close(jnp.sum((0.0 * x - y) ** 2), 56.0)
close(3 * mse(0.0, x, y), 56.0)
```

**Plausible wrong approach:** Comparing `jnp.sum` with `mse` directly fails because 56 is three times 56/3. The equality only holds after multiplying the mean by the observation count of three.

## Exercise 6: Transfer to new inputs

The same algebra transfers to new literal inputs. These two authored numbers are not an independent real-world evaluation dataset.

**Expected:** Predictions [8,10]; no population-quality claim.

```python
close(predict(2.0, jnp.array([4.0, 5.0])), [8.0, 10.0])
```

**Plausible wrong approach:** Reporting the predictions [8, 10] as evidence that weight 2 generalizes confuses arithmetic with evaluation. The inputs 4 and 5 were written by the author, so they test the multiplication, not data the rule has never seen.

## How to verify

Run `courses/jax/solutions/jax-001_solution.py` in the `jax-cpu` profile; the last line reads `jax-001: 8 asserted cases passed`. Independently, evaluate the closed form `14 * (w - 2) ** 2 / 3` at w = 0, 1 and 2 on paper and confirm 56/3, 14/3 and 0. Then pass `y[:, None]` to `mse` and confirm the ValueError, which shows the shape guard rather than broadcasting decided the result.

## Scope of this evidence

If a loss differs, inspect shapes and the denominator before changing tolerance. If a variable is undefined, reconstruct the complete program rather than assuming state survived an earlier Run. A successful import is not a passed numerical check.

Revisit python-05, python-16 and python-numpy-02 if function arguments or shapes are unfamiliar. Explain this fixture to another learner without using the word model as a substitute for the actual multiplication and reduction.
