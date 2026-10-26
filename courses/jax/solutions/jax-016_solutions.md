# jax-016: explained reference

For keep probability \(q\in(0,1]\), sample \(m_i\sim\operatorname{Bernoulli}(q)\) and return \(z_i=m_ix_i/q\) in training. Since \(\mathbb E[m_i]=q\), \(\mathbb E[z_i]=x_i\). Conditional on a fixed mask, \(\partial z_i/\partial x_i=m_i/q\). Evaluation returns \(z_i=x_i\). The boundary q=0 is undefined for this scaling and must be rejected before execution.

## Exercise 1: Replay a mask

Determinism supports debugging but is not independent fresh sampling.

**Expected:** Identical outputs.

```python
a = dropout(values, key, training=True)
b = dropout(values, key, training=True)
close(a, b)
```

## Exercise 2: Keep every activation

The Bernoulli mask is all true and the scale is one.

**Expected:** Output equals input.

```python
validate_keep(1.)
close(dropout(values, key, training=True, keep=1.), values)
```

## Exercise 3: Reject zero keep probability

Division by zero is not a usable all-dropped training policy under this contract.

**Expected:** ValueError.

```python
try:
    validate_keep(0.)
except ValueError:
    pass
else:
    raise AssertionError('zero keep accepted')
```

## Exercise 4: Differentiate with a fixed mask

The derivative is conditional on the supplied key's sampled mask; no derivative of the discrete key is requested.

**Expected:** Gradient coordinates equal the zero-or-two mask scaling.

```python
g = jax.grad(lambda x: dropout(x, key, training=True).sum())(values)
close(g, dropout(values, key, training=True))
```

## Exercise 5: Compile the mode policy

These are a small configuration set rather than per-element changing data.

**Expected:** Deterministic identity output.

```python
compiled = jax.jit(dropout, static_argnames=('training', 'keep'))
close(compiled(values, key, training=False, keep=.5), values)
```

## Exercise 6: Inspect a larger sample without a universal claim

The interval follows the output support. The expectation one is established algebraically, not guaranteed for this finite sample.

**Expected:** Finite mean between zero and two; every entry obeys the mask support.

```python
result = dropout(jnp.ones(4096), key, training=True)
mean = float(result.mean())
assert 0. <= mean <= 2.
assert bool(jnp.all((result == 0.) | (result == 2.)))
```

## Scope of this evidence

If evaluation changes with a random key, inspect the explicit mode path. If training repeats masks, inspect returned-key ownership. A fixed-mask gradient can be correct even though the random sampling operation itself is discrete.

Design a fair dropout comparison using a separate validation set and preserved key/state policy. Explain what additional evidence would support a generalization claim beyond the exact mask/scaling checks here.
