# jax-003: explained reference

Machine epsilon is the gap from 1 to the next larger representable value. For binary float32 it is \(2^{-23}\); for float64 it is \(2^{-52}\). A typical comparison accepts \(|a-b|\le\mathrm{atol}+\mathrm{rtol}|b|\). This is a chosen error contract, not a theorem about every algorithm. For log-sum-exp, subtracting \(m=\max_i z_i\) gives \(m+\log\sum_i e^{z_i-m}\); all exponentials are at most one.

## Exercise 1: Inspect precision

The header establishes policy before arrays exist; explicit dtype assertions make that assumption visible.

**Expected:** The requested two distinct dtypes are retained under the declared X64 policy.

```python
assert jnp.array([1.], dtype=jnp.float32).dtype == jnp.float32
assert jnp.array([1.], dtype=jnp.float64).dtype == jnp.float64
```

## Exercise 2: Calculate epsilon

Epsilon describes spacing near one, not constant spacing over the whole number line.

**Expected:** 2^-23 and 2^-52.

```python
assert float(jnp.finfo(jnp.float32).eps) == 2. ** -23
assert float(jnp.finfo(jnp.float64).eps) == 2. ** -52
```

## Exercise 3: Use an absolute bound

Near zero, the relative term contributes no useful allowance.

**Expected:** The explicit absolute-error check passes.

```python
close(jnp.float64(1e-12), 0., atol=2e-12, rtol=0.)
```

## Exercise 4: Keep counts exact

There is no statistical or floating approximation in this bounded integer count.

**Expected:** Scalar integer total 10.

```python
counts = jnp.array([2, 3, 5], dtype=jnp.int32)
assert counts.sum().shape == ()
assert int(counts.sum()) == 10
```

## Exercise 5: Shift scores safely

Adding a common offset changes log-normalization by that offset, while normalized probabilities would remain unchanged.

**Expected:** The values differ by exactly 1000 within tolerance.

```python
scores = jnp.array([0., math.log(3.)])
a = jax.scipy.special.logsumexp(scores)
b = jax.scipy.special.logsumexp(scores + 1000.)
close(a, math.log(4.))
close(b - a, 1000.)
```

## Exercise 6: Recognize invalid data

Tolerance is meaningful only after the declared numeric domain is satisfied.

**Expected:** Both fail the finite-value predicate.

```python
assert not bool(jnp.isfinite(jnp.array([jnp.nan, jnp.inf])).all())
```

## Scope of this evidence

When a check fails, inspect dtype, value scale, conditioning and intermediate overflow before widening tolerance. A float32-versus-float64 difference is not by itself an implementation defect. A wrong reduction or integer count remains wrong in either precision.

Connect this example to the numerical-accuracy discussion in the statistics and CUDA paths. Describe one computation where a stable formulation matters more than simply requesting another dtype, and state what hardware measurement would be needed for a performance conclusion.
