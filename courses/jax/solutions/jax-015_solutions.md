# jax-015: explained reference

For row inputs \(X\in\mathbb R^{N\times1}\), compute \(H=\tanh(XW_1+b_1)\) with \(W_1\in\mathbb R^{1\times4}\), then \(\widehat Y=HW_2+b_2\) with \(W_2\in\mathbb R^{4\times1}\). The model contains 4+4+4+1=13 parameters. Its mean loss reduces N scalar prediction events. The gradient tree must have the same structure and leaf shapes as those 13 parameters.

## Exercise 1: Replay initialization

The complete deterministic initialization policy, not only a label called seed, establishes this replay.

**Expected:** Matching tree structure and values.

```python
a = initialize(jax.random.key(31))
b = initialize(jax.random.key(31))
for x, y in zip(jax.tree.leaves(a), jax.tree.leaves(b)):
    close(x, y)
```

## Exercise 2: Inspect gradients

A particular zero bias gradient can be a symmetry of this data rather than a disconnected graph.

**Expected:** Matching parameter/gradient structures and shapes; finite gradients with nonzero total norm.

```python
p = initialize(jax.random.key(31))
g = jax.grad(objective)(p, train_x, train_y)
assert jax.tree.structure(p) == jax.tree.structure(g)
for a, b in zip(jax.tree.leaves(p), jax.tree.leaves(g)):
    assert a.shape == b.shape
    assert bool(jnp.isfinite(b).all())
assert sum(float(jnp.vdot(x, x)) for x in jax.tree.leaves(g)) > 0.
```

## Exercise 3: Check one compiled update

This is a compilation parity check with the same batch, reduction and learning rate.

**Expected:** Matching updated leaves.

```python
p = initialize(jax.random.key(31))
a, b = step(p, train_x, train_y), compiled_step(p, train_x, train_y)
for x, y in zip(jax.tree.leaves(a), jax.tree.leaves(b)):
    close(x, y)
```

## Exercise 4: Evaluate untouched inputs

The numerical value is an observation to report, not a threshold tuned on these final points.

**Expected:** A finite nonnegative held-out loss over exactly two targets.

```python
p = train()
value = objective(p, heldout_x, heldout_y)
assert heldout_x.shape[0] == 2
assert bool(jnp.isfinite(value)) and float(value) >= 0.
```

## Exercise 5: Separate training from inference

This model has no stochastic or mutable inference state. A later dropout model needs an explicit mode/key policy.

**Expected:** Matching deterministic predictions; no parameter update.

```python
p = train()
a, b = forward(p, heldout_x), forward(p, heldout_x)
close(a, b)
```

## Exercise 6: Check an architecture change

Each new hidden unit adds one input weight, one hidden bias and one output weight; the output bias is shared.

**Expected:** Width five would contain 16 parameters, three more than width four.

```python
count = lambda width: width + width + width + 1
assert count(4) == 13 and count(5) == 16
```

## Scope of this evidence

If training does not improve, inspect an exact one-step state, the objective reduction and the gradient tree before adjusting the budget. If held-out results disappoint, report them without retuning on those same points. Do not confuse the fixed synthetic target rule with an empirical population claim.

Port the one-step calculation to an existing framework route with matched initial arrays. Explain what an optimizer package or model library would add, then design a separate validation split before comparing widths or learning rates.
