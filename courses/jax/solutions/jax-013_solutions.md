# jax-013: explained reference

With C classes and active indicators \(m_i\), define \(L=-\frac{\sum_i m_i\log p_i(y_i)}{\sum_i m_i}\). For N active targets, the derivative of an active logit is \((p_{ij}-\mathbf1_{\{j=y_i\}})/N\). At uniform three-class probabilities and three active targets, true-class coordinates have derivative \(-2/9\), other coordinates \(1/9\), and ignored rows zero. An all-ignored batch has no defined empirical mean.

## Solution approach

Split the work between two functions with different jobs. `admit` runs on the host with NumPy and rejects malformed inputs before any loss exists: wrong shapes, a non-Boolean or empty mask, or an active label outside the classes. `token_mean` is pure JAX: it replaces inactive labels with 0, gathers the log-softmax of each target, zeroes inactive rows, and divides by the active count.

**Why it is correct here:** Uniform logits over three classes give probability 1/3 for every target, so each active row costs log 3 and their mean is log 3 regardless of padding. For logits [log 3, 0] the softmax is [3/4, 1/4], so target 0 costs log(4/3) and target 1 costs log 4. For [1000, 0, -1000] the target already holds nearly all the mass, so the loss is close to zero.

## Exercise 1: Append ignored storage

Padding is not evidence and does not change the active count.

**Expected:** Still log(3).

```python
padded = jnp.zeros((6, 3))
labels = jnp.array([0, 1, 2, -100, -100, -100])
mask = jnp.array([True, True, True, False, False, False])
admit(padded, labels, mask)
close(token_mean(padded, labels, mask), math.log(3.0))
```

**Plausible wrong approach:** Dividing by the number of stored rows instead of `active.sum()` turns the padded fixture into `3 * log 3 / 6`, half the correct value. Padding would then change the objective it should not affect.

## Exercise 2: Reject an empty objective

A zero denominator cannot be reinterpreted as perfect prediction.

**Expected:** ValueError before loss reduction.

```python
try:
    admit(logits, targets, jnp.zeros(4, dtype=bool))
except ValueError:
    pass
else:
    raise AssertionError("empty supervision accepted")
```

**Plausible wrong approach:** Skipping `admit` for an all-false mask lets `token_mean` compute 0 / 0, which is NaN rather than an error. Reporting zero instead would claim perfect prediction with no evidence.

## Exercise 3: Check target identity

A nonuniform row detects a target swap that the uniform fixture could hide.

**Expected:** Losses log(4/3) and log(4).

```python
scores = jnp.array([[math.log(3.0), 0.0]])
mask = jnp.array([True])
close(token_mean(scores, jnp.array([0]), mask), math.log(4 / 3))
close(token_mean(scores, jnp.array([1]), mask), math.log(4.0))
```

**Plausible wrong approach:** Checking target identity only on the uniform fixture cannot catch a label swap, since every class scores log 3 there. The nonuniform row separates log(4/3) from log 4.

## Exercise 4: Keep an extreme logit finite

Stable log-softmax avoids an unnecessary exponential overflow.

**Expected:** Finite loss near zero.

```python
value = token_mean(jnp.array([[1000.0, 0.0, -1000.0]]), jnp.array([0]), jnp.array([True]))
assert bool(jnp.isfinite(value))
close(value, 0.0)
```

**Plausible wrong approach:** Computing `jnp.log(jnp.exp(z) / jnp.exp(z).sum())` overflows `exp(1000)` to infinity and returns NaN. `jax.nn.log_softmax` subtracts the row maximum first.

## Exercise 5: Reject an active sentinel

The sentinel is only permitted outside the supervised target set.

**Expected:** ValueError.

```python
try:
    admit(logits, targets, jnp.ones(4, dtype=bool))
except ValueError:
    pass
else:
    raise AssertionError("active sentinel accepted")
```

**Plausible wrong approach:** Relying on the gather to fail for the active label -100 does not work, because JAX does not raise index errors for out-of-range gathers. The host-side bounds check in `admit` is what rejects it.

## Exercise 6: Compile the validated calculation

The host-side validation check and pure numerical loss have distinct execution roles.

**Expected:** Same log(3) value.

```python
admit(logits, targets, active)
close(jax.jit(token_mean)(logits, targets, active), math.log(3.0))
```

**Plausible wrong approach:** Calling `admit` inside the function passed to `jax.jit` fails, because `np.asarray` cannot convert a tracer to a concrete array. Validation belongs before the compiled call, as the reference does.

## How to verify

After the reference prints `jax-013: 8 asserted cases passed`, line up `token_mean` with `-jax.nn.log_softmax(logits)[jnp.arange(3), targets[:3]].mean()` on the first three rows to confirm the mask removes only the sentinel. Then pass integer zeros as the mask and confirm `admit` reports the Boolean requirement.

## Scope of this evidence

A suspiciously small loss can come from a wrong denominator, wrong class axis or masking after an invalid operation. Inspect active target identities and direct gradients. The host-side validation function is intentionally not a transformed numerical kernel.

Map this objective to shifted next-token labels in llm-017 and llm-031. Explain why excluding prompt targets does not imply zero gradient through all prompt representations in a full causal model.
