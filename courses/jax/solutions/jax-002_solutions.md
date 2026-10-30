# jax-002: explained reference

For \(X\in\mathbb R^{2\times3}\), row sums satisfy \(r_i=\sum_{j=0}^{2}X_{ij}\) and column sums satisfy \(c_j=\sum_{i=0}^{1}X_{ij}\). Row centering is \(X_{ij}-\frac13\sum_kX_{ik}\). Keeping the reduced axis as a singleton makes the subtraction's intended broadcast visible. The centered row sums should be zero, which is a stronger oracle than checking only the output shape.

## Exercise 1: Center each observation

keepdims retains shape (2,1), so each row receives its own mean.

**Expected:** Both rows [-1,0,1]; row sums zero.

```python
centered = table - table.mean(axis=1, keepdims=True)
close(centered, [[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]])
close(centered.sum(axis=1), [0.0, 0.0])
```

## Exercise 2: Broadcast feature offsets

The three offsets align with the final dimension.

**Expected:** [[10,21,32],[13,24,35]].

```python
close(table + jnp.array([10.0, 20.0, 30.0]), [[10.0, 21.0, 32.0], [13.0, 24.0, 35.0]])
```

## Exercise 3: Broadcast observation offsets

A (2,1) array repeats each offset across that row's features.

**Expected:** [[10,11,12],[23,24,25]].

```python
close(table + jnp.array([10.0, 20.0])[:, None], [[10.0, 11.0, 12.0], [23.0, 24.0, 25.0]])
```

## Exercise 4: Accumulate an update

add expresses an increment, whereas set replaces the old value.

**Expected:** New [6,2], original [1,2].

```python
old = jnp.array([1.0, 2.0])
close(old.at[0].add(5.0), [6.0, 2.0])
close(old, [1.0, 2.0])
```

## Exercise 5: Enforce the index boundary

The lesson refuses this request explicitly rather than relying on backend-specific bounds behavior.

**Expected:** ValueError from the declared host-side guard.

```python
try:
    replace_at(jnp.zeros(3), 3, 1.0)
except ValueError:
    pass
else:
    raise AssertionError("bad index accepted")
```

## Exercise 6: Transfer the axis rule

Changing both axis lengths catches implementations that accidentally relied on a square or fixed-size example.

**Expected:** Shape (3,2), all row sums zero.

```python
other = jnp.arange(6.0).reshape(3, 2)
centered = other - other.mean(axis=1, keepdims=True)
assert centered.shape == (3, 2)
close(centered.sum(axis=1), jnp.zeros(3))
```

## Scope of this evidence

A shape-correct result may still reduce the wrong population. Check a row-specific invariant and use nonsquare fixtures. Keep index admission outside transformed numerical code until the tracing rules have been taught.

Compare this value-oriented update with NumPy mutation in python-numpy-01. Explain why an implementation's possible in-place optimization does not make arbitrary Python mutation part of JAX's public array contract.
