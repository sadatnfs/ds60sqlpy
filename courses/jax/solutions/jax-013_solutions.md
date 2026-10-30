# jax-013: explained reference

With C classes and active indicators \(m_i\), define \(L=-\frac{\sum_i m_i\log p_i(y_i)}{\sum_i m_i}\). For N active targets, the derivative of an active logit is \((p_{ij}-\mathbf1_{\{j=y_i\}})/N\). At uniform three-class probabilities and three active targets, true-class coordinates have derivative \(-2/9\), other coordinates \(1/9\), and ignored rows zero. An all-ignored batch has no defined empirical mean.

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

## Exercise 3: Check target identity

A nonuniform row detects a target swap that the uniform fixture could hide.

**Expected:** Losses log(4/3) and log(4).

```python
scores = jnp.array([[math.log(3.0), 0.0]])
mask = jnp.array([True])
close(token_mean(scores, jnp.array([0]), mask), math.log(4 / 3))
close(token_mean(scores, jnp.array([1]), mask), math.log(4.0))
```

## Exercise 4: Keep an extreme logit finite

Stable log-softmax avoids an unnecessary exponential overflow.

**Expected:** Finite loss near zero.

```python
value = token_mean(jnp.array([[1000.0, 0.0, -1000.0]]), jnp.array([0]), jnp.array([True]))
assert bool(jnp.isfinite(value))
close(value, 0.0)
```

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

## Exercise 6: Compile the admitted calculation

The host admission check and pure numerical loss have distinct execution roles.

**Expected:** Same log(3) value.

```python
admit(logits, targets, active)
close(jax.jit(token_mean)(logits, targets, active), math.log(3.0))
```

## Scope of this evidence

A suspiciously small loss can come from a wrong denominator, wrong class axis or masking after an invalid operation. Inspect active target identities and direct gradients. The host admission function is intentionally not a transformed numerical kernel.

Map this objective to shifted next-token labels in llm-017 and llm-031. Explain why excluding prompt targets does not imply zero gradient through all prompt representations in a full causal model.
