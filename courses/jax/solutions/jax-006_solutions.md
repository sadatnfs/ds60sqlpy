# jax-006: explained reference

For corresponding parameter and gradient trees \(P\) and \(G\), an SGD map applies \(P'_\ell=P_\ell-\eta G_\ell\) at every leaf \(\ell\). The index denotes a tree leaf, not an array coordinate. Within a leaf the ordinary array shape contract still applies. A correct tree-level match does not prevent a gradient with a broadcastable but unintended leaf shape, so verify both structure and each leaf's shape.

## Exercise 1: Inspect the leaf ledger

This ledger explains which arrays a later transformation will receive.

**Expected:** Weight (2,2), bias (2,).

```python
shapes = jax.tree.map(lambda x: x.shape, params)
assert shapes == {"weight": (2, 2), "bias": (2,)}
```

## Exercise 2: Count stored scalars

The count is four matrix entries plus two biases, not the number of containers.

**Expected:** Six scalar entries.

```python
assert sum(x.size for x in jax.tree.leaves(params)) == 6
```

## Exercise 3: Reconstruct the tree

The structure descriptor preserves how leaves belong to containers.

**Expected:** Same structure and values.

```python
leaves, structure = jax.tree.flatten(params)
restored = jax.tree.unflatten(structure, leaves)
assert jax.tree.structure(restored) == jax.tree.structure(params)
close(restored["weight"], params["weight"])
```

## Exercise 4: Reject a missing field

A smaller gradient tree does not describe an update for every parameter under this contract.

**Expected:** ValueError before mapping.

```python
try:
    checked_update(params, {"weight": jnp.ones((2, 2))}, 0.1)
except ValueError:
    pass
else:
    raise AssertionError("missing leaf accepted")
```

## Exercise 5: Apply distinct gradients

Leaf correspondence preserves which gradient belongs to which parameter.

**Expected:** Weight [[0,1],[2,3]], bias [-0.5,1].

```python
g = {"weight": jnp.full((2, 2), 2.0), "bias": jnp.array([3.0, -4.0])}
u = checked_update(params, g, 0.5)
close(u["weight"], [[0.0, 1.0], [2.0, 3.0]])
close(u["bias"], [-0.5, 1.0])
```

## Exercise 6: Transfer to nested state

The mechanism is about nested numerical state, not only one model dictionary.

**Expected:** Same structure; all seven numerical entries zero.

```python
state = (params, jnp.int64(4))
zero = jax.tree.map(jnp.zeros_like, state)
assert jax.tree.structure(zero) == jax.tree.structure(state)
assert all(bool(jnp.all(x == 0)) for x in jax.tree.leaves(zero))
```

## Scope of this evidence

A mismatch can come from container structure, leaf shape, dtype or semantic identity. Diagnose them separately. Do not assume that every leaf in a state tree should receive a gradient or optimizer update; counters and random keys have different roles.

Design separate parameter, optimizer and diagnostic trees for a two-layer model. Explain what must be preserved to resume one update and which metadata should remain static. Compare this explicit representation with registered parameter objects in torch-003.
