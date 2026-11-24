# jax-005: explained reference

Write a stochastic computation as a deterministic map \((k,x)\mapsto y\). A transition can first compute \((k_{\mathrm{next}},k_{\mathrm{draw}})=\operatorname{split}(k)\), then evaluate the draw with \(k_{\mathrm{draw}}\) and return \(k_{\mathrm{next}}\). No derivative is taken with respect to a key. Reproducibility requires the key, random operation, shape, dtype and relevant implementation version, not just a printed scalar sample.

## Solution approach

Treat every random draw as a pure function of a key. `draw_step` splits its key into a key to carry forward and a key to consume, draws four normals with the consumed key, and returns both. Each task then asks a question about key identity, which `same_key` answers by comparing the raw `key_data` arrays rather than sampled values.

**Why it is correct here:** The same root and the same `fold_in` identifier always produce the same key, so identifier 42 replays and identifier 43 differs. `split` into four yields four keys with distinct data. The sequence function starts from `key(19)` and applies the same three transitions both times, so its final keys and stacked (3, 4) draws must match.

## Exercise 1: Inspect a typed key

The typed key is not an ordinary floating scalar. Its representation is exposed for inspection or explicit serialization boundaries.

**Expected:** Key shape (); key_data is an integer array.

```python
key = jax.random.key(11)
assert key.shape == ()
assert np.issubdtype(np.asarray(jax.random.key_data(key)).dtype, np.integer)
```

**Plausible wrong approach:** Checking `isinstance(key, float)` or printing the key tells little about its representation. The typed key has shape () and its contents are integer words reached through `jax.random.key_data`.

## Exercise 2: Split four streams

This checks allocation of streams, not a statistical theorem based on four observed numbers.

**Expected:** Four distinct key identities in the declared split.

```python
keys = jax.random.split(jax.random.key(11), 4)
assert keys.shape == (4,)
assert len({np.asarray(jax.random.key_data(k)).tobytes() for k in keys}) == 4
```

**Plausible wrong approach:** Comparing four uniform draws for distinctness tests sampled values, which could collide by chance. The task checks stream allocation, so the reference compares the bytes of each key's data.

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

**Plausible wrong approach:** Deriving a record key with `jax.random.key(3 + 42)` mixes the root seed and record identifier into one integer, so root 4 with record 41 would collide. `fold_in` keeps the two inputs separate.

## Exercise 4: Separate identities

A changed identity receives a separate deterministic stream under this policy.

**Expected:** Different key data.

```python
root = jax.random.key(3)
assert not same_key(jax.random.fold_in(root, 42), jax.random.fold_in(root, 43))
```

**Plausible wrong approach:** Testing that draws from records 42 and 43 differ in their first value is weak: two floats could coincide. Comparing key data states the property that actually separates the two streams.

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

**Plausible wrong approach:** Writing `draw_step(key)` without rebinding `key` in the loop reuses the same key three times, producing three identical rows. The returned next key must replace the old one at every step.

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

**Plausible wrong approach:** Reading two equal Bernoulli masks as bad luck misses the cause: the same key always gives the same eight values. After `split`, `k1` and `k2` differ even if some mask entries still match.

## How to verify

Run the reference and expect `jax-005: 8 asserted cases passed`. As an extra check, draw `jax.random.uniform(jax.random.key(11), (3,))` twice in one script and confirm equality, then draw from `jax.random.split(jax.random.key(11))[0]` and confirm the values change. Inspect the `(3, 4)` shape of the stacked sequence draws before comparing their values.

## Scope of this evidence

Repeated randomness often comes from discarding the returned key or broadcasting one key over all examples. Unexpected non-replay can come from changed shape, dtype, split order or version. Do not promise cross-version bitwise identity without an explicit tested contract.

Design a stream policy for a simulation with independent records and repeated steps. Name what stays reproducible if record order changes, then explain how that policy differs from consuming one sequential stream. Connect the result to cuda-050 without claiming GPU execution.
