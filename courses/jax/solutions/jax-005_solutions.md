# jax-005: explained reference

Write a stochastic computation as a deterministic map \((k,x)\mapsto y\). A transition can first compute \((k_{\mathrm{next}},k_{\mathrm{draw}})=\operatorname{split}(k)\), then evaluate the draw with \(k_{\mathrm{draw}}\) and return \(k_{\mathrm{next}}\). No derivative is taken with respect to a key. Reproducibility requires the key, random operation, shape, dtype and relevant implementation version, not just a printed scalar sample.

## Exercise 1: Inspect a typed key

The typed key is not an ordinary floating scalar. Its representation is exposed for inspection or explicit serialization boundaries.

**Expected:** Key shape (); key_data is an integer array.

```python
key = jax.random.key(11)
assert key.shape == ()
assert np.issubdtype(np.asarray(jax.random.key_data(key)).dtype, np.integer)
```

## Exercise 2: Split four streams

This checks allocation of streams, not a statistical theorem based on four observed numbers.

**Expected:** Four distinct key identities in the declared split.

```python
keys = jax.random.split(jax.random.key(11), 4)
assert keys.shape == (4,)
assert len({np.asarray(jax.random.key_data(k)).tobytes() for k in keys}) == 4
```

## Exercise 3: Replay a record identity

The association is deterministic when both root and identifier agree.

**Expected:** Identical folded keys and draws.

```python
root = jax.random.key(3)
a = jax.random.fold_in(root, 42)
b = jax.random.fold_in(root, 42)
assert same_key(a, b)
close(jax.random.uniform(a, (3,)), jax.random.uniform(b, (3,)))
```

## Exercise 4: Separate identities

A changed identity receives a separate deterministic stream under this policy.

**Expected:** Different key data.

```python
root = jax.random.key(3)
assert not same_key(jax.random.fold_in(root, 42), jax.random.fold_in(root, 43))
```

## Exercise 5: Replay a whole transition

A sequence is reproducible when its transition and starting state are the same.

**Expected:** All corresponding draws and final keys agree.

```python
def sequence():
    key = jax.random.key(19)
    values = []
    for _ in range(3):
        key, value = draw_step(key)
        values.append(value)
    return key, jnp.stack(values)


a, x = sequence()
b, y = sequence()
assert same_key(a, b)
close(x, y)
```

## Exercise 6: Diagnose repeated example masks

The defect is key reuse when independence was intended, not the coincidence of individual Boolean values.

**Expected:** Same-key masks repeat; split keys are distinct even if some sampled mask entries coincide.

```python
key = jax.random.key(5)
a = jax.random.bernoulli(key, 0.5, (8,))
b = jax.random.bernoulli(key, 0.5, (8,))
assert np.array_equal(np.asarray(a), np.asarray(b))
k1, k2 = jax.random.split(key)
assert not same_key(k1, k2)
```

## Scope of this evidence

Repeated randomness often comes from discarding the returned key or broadcasting one key over all examples. Unexpected non-replay can come from changed shape, dtype, split order or version. Do not promise cross-version bitwise identity without an explicit tested contract.

Design a stream policy for a simulation with independent records and repeated steps. Name what stays reproducible if record order changes, then explain how that policy differs from consuming one sequential stream. Connect the result to cuda-050 without claiming GPU execution.
