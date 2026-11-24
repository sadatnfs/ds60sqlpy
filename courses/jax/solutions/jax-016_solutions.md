# jax-016: explained reference

For keep probability \(q\in(0,1]\), sample \(m_i\sim\operatorname{Bernoulli}(q)\) and return \(z_i=m_ix_i/q\) in training. Since \(\mathbb E[m_i]=q\), \(\mathbb E[z_i]=x_i\). Conditional on a fixed mask, \(\partial z_i/\partial x_i=m_i/q\). Evaluation returns \(z_i=x_i\). The boundary q=0 is undefined for this scaling and must be rejected before execution.

## Solution approach

Write the dropout contract before any sampling: in training mode a Bernoulli mask with probability `keep` chooses which entries survive, and survivors are divided by `keep` so the expected value is unchanged. In evaluation mode the input passes through untouched. With an input of ones and keep 0.5, every output entry is therefore either 0 or 2.

**Why it is correct here:** One key always produces one mask, so two calls agree. Keep 1 makes the mask all true and the scale one. `validate_keep` rejects 0 because the interval is open at zero. The derivative of `sum(where(mask, x / keep, 0))` is `mask / keep`, which equals the dropped output of a ones vector. Every entry of the 4096 sample lies in {0, 2}, so the mean lies in [0, 2].

## Exercise 1: Replay a mask

Determinism supports debugging but is not independent fresh sampling.

**Expected:** Identical outputs.

```python
a = dropout(values, key, training=True)
b = dropout(values, key, training=True)
close(a, b)
```

**Plausible wrong approach:** Expecting two training calls to differ because dropout is random confuses sampling with key management. A new mask needs a new key, usually from `jax.random.split`; the same key replays the same mask.

## Exercise 2: Keep every activation

The Bernoulli mask is all true and the scale is one.

**Expected:** Output equals input.

```python
validate_keep(1.0)
close(dropout(values, key, training=True, keep=1.0), values)
```

**Plausible wrong approach:** Applying the mask without dividing by `keep` gives outputs of 0 or 1 and halves the expected activation. With keep 1 that bug is invisible, which is why the fixture uses 0.5 elsewhere.

## Exercise 3: Reject zero keep probability

Division by zero is not a usable all-dropped training policy under this contract.

**Expected:** ValueError.

```python
try:
    validate_keep(0.0)
except ValueError:
    pass
else:
    raise AssertionError("zero keep accepted")
```

**Plausible wrong approach:** Allowing keep 0 seems to mean drop everything, but the survivor scale `1 / keep` is infinite. Even though the output would be all zeros, the scale factor poisons derivatives, so the lesson rejects it.

## Exercise 4: Differentiate with a fixed mask

The derivative is conditional on the supplied key's sampled mask; no derivative of the discrete key is requested.

**Expected:** Gradient coordinates equal the zero-or-two mask scaling.

```python
g = jax.grad(lambda x: dropout(x, key, training=True).sum())(values)
close(g, dropout(values, key, training=True))
```

**Plausible wrong approach:** Treating dropout as the identity when differentiating predicts a gradient of all ones. The gradient is the sampled mask divided by keep, so dropped entries contribute zero and survivors contribute two.

## Exercise 5: Compile the mode policy

These are a small configuration set rather than per-element changing data.

**Expected:** Deterministic identity output.

```python
compiled = jax.jit(dropout, static_argnames=("training", "keep"))
close(compiled(values, key, training=False, keep=0.5), values)
```

**Plausible wrong approach:** Compiling with `jax.jit(dropout)` and no static arguments fails at `if not training`, since a traced Boolean cannot drive Python control flow. Marking `training` and `keep` static fixes that.

## Exercise 6: Inspect a larger sample without a universal claim

The interval follows the output support. The expectation one is established algebraically, not guaranteed for this finite sample.

**Expected:** Finite mean between zero and two; every entry obeys the mask support.

```python
result = dropout(jnp.ones(4096), key, training=True)
mean = float(result.mean())
assert 0.0 <= mean <= 2.0
assert bool(jnp.all((result == 0.0) | (result == 2.0)))
```

**Plausible wrong approach:** Asserting that the mean of the 4096 sample equals one treats an expectation as a guarantee. The sample mean has a standard error of about 1/64, so only the support bound is safe to assert.

## How to verify

Run the reference and confirm `jax-016: 8 asserted cases passed`. Print `dropout(values, key, training=True)` and check that it holds only zeros and twos. Then replace the key with `jax.random.split(key)[1]` and confirm the mask changes, while `training=False` still returns the ones vector exactly.

## Scope of this evidence

If evaluation changes with a random key, inspect the explicit mode path. If training repeats masks, inspect returned-key ownership. A fixed-mask gradient can be correct even though the random sampling operation itself is discrete.

Design a fair dropout comparison using a separate validation set and preserved key/state policy. Explain what additional evidence would support a generalization claim beyond the exact mask/scaling checks here.
