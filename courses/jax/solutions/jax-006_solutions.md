# jax-006: explained reference

For corresponding parameter and gradient trees \(P\) and \(G\), an SGD map applies \(P'_\ell=P_\ell-\eta G_\ell\) at every leaf \(\ell\). The index denotes a tree leaf, not an array coordinate. Within a leaf the ordinary array shape contract still applies. A correct tree-level match does not prevent a gradient with a broadcastable but unintended leaf shape, so verify both structure and each leaf's shape.

## Solution approach

Treat `params` as a ledger of named arrays: a (2, 2) weight and a (2,) bias. Each task either reads that ledger with `jax.tree.map` and `jax.tree.leaves`, or pairs it with a second tree of the same structure. `checked_update` refuses to pair trees until both the structure and every leaf shape agree, and only then applies `p - rate * g` leaf by leaf.

**Why it is correct here:** The weight holds four entries and the bias two, so the scalar count is six. With gradient 2 everywhere on the weight and rate 0.5, each weight entry drops by 1, turning [[1, 2], [3, 4]] into [[0, 1], [2, 3]]. The bias [1, -1] minus 0.5 times [3, -4] is [-0.5, 1]. Adding the scalar counter to the tuple makes seven zeroed entries.

## Exercise 1: Inspect the leaf ledger

This ledger explains which arrays a later transformation will receive.

**Expected:** Weight (2,2), bias (2,).

```python
shapes = jax.tree.map(lambda x: x.shape, params)
assert shapes == {"weight": (2, 2), "bias": (2,)}
```

**Plausible wrong approach:** Mapping `len` over the leaves reports 2 for both arrays, because the weight has two rows and the bias two entries. Only `.shape` distinguishes the (2, 2) matrix from the (2,) vector.

## Exercise 2: Count stored scalars

The count is four matrix entries plus two biases, not the number of containers.

**Expected:** Six scalar entries.

```python
assert sum(x.size for x in jax.tree.leaves(params)) == 6
```

**Plausible wrong approach:** Counting `len(jax.tree.leaves(params))` gives 2, the number of arrays, not 6. The question asks for stored scalars, so each leaf's `.size` must be summed.

## Exercise 3: Reconstruct the tree

The structure descriptor preserves how leaves belong to containers.

**Expected:** Same structure and values.

```python
leaves, structure = jax.tree.flatten(params)
restored = jax.tree.unflatten(structure, leaves)
assert jax.tree.structure(restored) == jax.tree.structure(params)
close(restored["weight"], params["weight"])
```

**Plausible wrong approach:** Rebuilding the dictionary as `dict(zip(params.keys(), leaves))` swaps the arrays: JAX flattens dictionaries in sorted key order, bias before weight, while `params.keys()` follows insertion order, weight first.

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

**Plausible wrong approach:** Zipping leaves without the structure check pairs the bias (2,) with the only gradient leaf, the (2, 2) weight gradient. Broadcasting then returns a (2, 2) bias with no error, which is why the tree structure is compared first.

## Exercise 5: Apply distinct gradients

Leaf correspondence preserves which gradient belongs to which parameter.

**Expected:** Weight [[0,1],[2,3]], bias [-0.5,1].

```python
g = {"weight": jnp.full((2, 2), 2.0), "bias": jnp.array([3.0, -4.0])}
u = checked_update(params, g, 0.5)
close(u["weight"], [[0.0, 1.0], [2.0, 3.0]])
close(u["bias"], [-0.5, 1.0])
```

**Plausible wrong approach:** Adding the step instead of subtracting it gives weight [[2, 3], [4, 5]] and bias [2.5, -3]. The values look plausible, so only the asserted numbers catch the sign error.

## Exercise 6: Transfer to nested state

The mechanism is about nested numerical state, not only one model dictionary.

**Expected:** Same structure; all seven numerical entries zero.

```python
state = (params, jnp.int64(4))
zero = jax.tree.map(jnp.zeros_like, state)
assert jax.tree.structure(zero) == jax.tree.structure(state)
assert all(bool(jnp.all(x == 0)) for x in jax.tree.leaves(zero))
```

**Plausible wrong approach:** Calling `jnp.zeros_like(state)` on the whole tuple tries to turn a dictionary and a scalar into one array and fails. `jax.tree.map` applies `zeros_like` to each of the three leaves separately.

## How to verify

Run the reference and look for `jax-006: 8 asserted cases passed`. Print `jax.tree.leaves(params)` and note that the bias appears first, which explains the key-order trap. Then call `checked_update` with a gradient whose bias has shape (3,) and confirm the leaf-shape ValueError, proving both guards run before any arithmetic.

## Scope of this evidence

A mismatch can come from container structure, leaf shape, dtype or semantic identity. Diagnose them separately. Do not assume that every leaf in a state tree should receive a gradient or optimizer update; counters and random keys have different roles.

Design separate parameter, optimizer and diagnostic trees for a two-layer model. Explain what must be preserved to resume one update and which metadata should remain static. Compare this explicit representation with registered parameter objects in torch-003.
