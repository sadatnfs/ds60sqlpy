# jax-003: explained reference

Machine epsilon is the gap from 1 to the next larger representable value. For binary float32 it is \(2^{-23}\); for float64 it is \(2^{-52}\). A typical comparison accepts \(|a-b|\le\mathrm{atol}+\mathrm{rtol}|b|\). This is a chosen error contract, not a theorem about every algorithm. For log-sum-exp, subtracting \(m=\max_i z_i\) gives \(m+\log\sum_i e^{z_i-m}\); all exponentials are at most one.

## Solution approach

The header turns on 64-bit mode before any array exists, so every dtype in this lesson is requested explicitly and then asserted. Each task isolates one numerical fact: the dtype that was kept, the epsilon of each float format, an absolute-only tolerance near zero, an exact integer count, the shift identity of log-sum-exp and a finite-value precondition.

**Why it is correct here:** Epsilon for float32 is exactly `2.0**-23` and for float64 exactly `2.0**-52`, so equality rather than closeness is appropriate. The scores 0 and log 3 exponentiate to 1 and 3, whose sum is 4, giving `logsumexp = log 4`. Adding 1000 to both scores multiplies each exponential by the same factor, which adds exactly 1000 to the log of the sum.

## Exercise 1: Inspect precision

The header establishes policy before arrays exist; explicit dtype assertions make that assumption visible.

**Expected:** The requested two distinct dtypes are retained under the declared X64 policy.

```python
assert jnp.array([1.0], dtype=jnp.float32).dtype == jnp.float32
assert jnp.array([1.0], dtype=jnp.float64).dtype == jnp.float64
```

**Plausible wrong approach:** Checking only `jnp.array([1.0]).dtype` shows float64 under the X64 header and float32 without it, so it tests the global setting rather than the requested dtype. Passing `dtype=` explicitly is what makes both assertions meaningful.

## Exercise 2: Calculate epsilon

Epsilon describes spacing near one, not constant spacing over the whole number line.

**Expected:** 2^-23 and 2^-52.

```python
assert float(jnp.finfo(jnp.float32).eps) == 2.0**-23
assert float(jnp.finfo(jnp.float64).eps) == 2.0**-52
```

**Plausible wrong approach:** Treating epsilon as the absolute error of any float32 result is wrong: near 1000 the spacing of float32 values is `2**-14`, 512 times larger than `2**-23`, because spacing scales with the binary exponent.

## Exercise 3: Use an absolute bound

Near zero, the relative term contributes no useful allowance.

**Expected:** The explicit absolute-error check passes.

```python
close(jnp.float64(1e-12), 0.0, atol=2e-12, rtol=0.0)
```

**Plausible wrong approach:** Using the default relative tolerance to compare 1e-12 with 0.0 fails because `rtol * |0|` is zero. Without an explicit `atol`, any nonzero residual near zero is rejected no matter how small.

## Exercise 4: Keep counts exact

There is no statistical or floating approximation in this bounded integer count.

**Expected:** Scalar integer total 10.

```python
counts = jnp.array([2, 3, 5], dtype=jnp.int32)
assert counts.sum().shape == ()
assert int(counts.sum()) == 10
```

**Plausible wrong approach:** Summing the counts after casting them to float32 still returns 10.0 here, but it turns an exact integer total into an approximate one and changes the scalar dtype, so the `int` comparison no longer documents exactness.

## Exercise 5: Shift scores safely

Adding a common offset changes log-normalization by that offset, while normalized probabilities would remain unchanged.

**Expected:** The values differ by exactly 1000 within tolerance.

```python
scores = jnp.array([0.0, math.log(3.0)])
a = jax.scipy.special.logsumexp(scores)
b = jax.scipy.special.logsumexp(scores + 1000.0)
close(a, math.log(4.0))
close(b - a, 1000.0)
```

**Plausible wrong approach:** Computing `jnp.log(jnp.sum(jnp.exp(scores + 1000.0)))` directly overflows, because `exp(1000)` exceeds the float64 range and returns inf. The library subtracts the maximum first, which keeps every exponential at most one.

## Exercise 6: Recognize invalid data

Tolerance is meaningful only after the declared numeric domain is satisfied.

**Expected:** Both fail the finite-value predicate.

```python
assert not bool(jnp.isfinite(jnp.array([jnp.nan, jnp.inf])).all())
```

**Plausible wrong approach:** Comparing NaN and inf with a wide tolerance does not make them valid. `assert_allclose` treats matching NaNs as equal by default, so the `isfinite` check must run before any tolerance is applied.

## How to verify

Run the reference and expect `jax-003: 8 asserted cases passed`. Then print `jnp.finfo(jnp.float32).eps` and `jnp.finfo(jnp.float64).eps` and compare them with `2.0**-23` and `2.0**-52`. Evaluate the unstable `log(sum(exp(scores + 1000)))` once to see inf, and contrast it with the `logsumexp` difference of 1000 to confirm why the stable form is used.

## Scope of this evidence

When a check fails, inspect dtype, value scale, conditioning and intermediate overflow before widening tolerance. A float32-versus-float64 difference is not by itself an implementation defect. A wrong reduction or integer count remains wrong in either precision.

Connect this example to the numerical-accuracy discussion in the statistics and CUDA paths. Describe one computation where a stable formulation matters more than simply requesting another dtype, and state what hardware measurement would be needed for a performance conclusion.
