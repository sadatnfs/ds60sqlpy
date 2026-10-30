# jax-001: explained reference

For inputs \(x_i\), targets \(y_i\) and scalar weight \(w\), define \(\widehat y_i=wx_i\) and \(L(w)=N^{-1}\sum_i(\widehat y_i-y_i)^2\). The denominator counts observations because each observation has one output here. With several output coordinates, a mean over every array entry would answer a different weighting question. At \(w=0\), the three residual squares sum to 56 and the loss is \(56/3\). At \(w=2\), every residual is zero. Neither calculation uses a gradient or updates a parameter.

## Exercise 1: Trace another predictor

Each error equals minus the corresponding input; square and average.

**Expected:** [1,2,3] and 14/3.

```python
close(predict(1.0, x), [1.0, 2.0, 3.0])
close(mse(1.0, x, y), 14 / 3)
```

## Exercise 2: Construct an exact fit

All targets follow the same declared rule, so this is an algebraic fit to the fixture.

**Expected:** Weight 2 gives zero loss.

```python
close(mse(2.0, x, y), 0.0)
```

## Exercise 3: Change the target

Only the final target differs by one; the denominator remains three.

**Expected:** Loss 1/3.

```python
close(mse(2.0, x, jnp.array([2.0, 4.0, 7.0])), 1 / 3)
```

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

## Exercise 5: Separate sum from mean

The equality relies on exactly three equally weighted output entries.

**Expected:** Both are 56.

```python
close(jnp.sum((0.0 * x - y) ** 2), 56.0)
close(3 * mse(0.0, x, y), 56.0)
```

## Exercise 6: Transfer to new inputs

The same algebra transfers to new literal inputs. These two authored numbers are not an independent real-world evaluation dataset.

**Expected:** Predictions [8,10]; no population-quality claim.

```python
close(predict(2.0, jnp.array([4.0, 5.0])), [8.0, 10.0])
```

## Scope of this evidence

If a loss differs, inspect shapes and the denominator before changing tolerance. If a variable is undefined, reconstruct the complete program rather than assuming state survived an earlier Run. A successful import is not a passed numerical check.

Revisit python-05, python-16 and python-numpy-02 if function arguments or shapes are unfamiliar. Explain this fixture to another learner without using the word model as a substitute for the actual multiplication and reduction.
