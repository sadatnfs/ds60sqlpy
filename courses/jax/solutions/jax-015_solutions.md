# jax-015: explained reference

For row inputs \(X\in\mathbb R^{N\times1}\), compute \(H=\tanh(XW_1+b_1)\) with \(W_1\in\mathbb R^{1\times4}\), then \(\widehat Y=HW_2+b_2\) with \(W_2\in\mathbb R^{4\times1}\). The model contains 4+4+4+1=13 parameters. Its mean loss reduces N scalar prediction events. The gradient tree must have the same structure and leaf shapes as those 13 parameters.

## Solution approach

Keep the network small enough to audit: a (1, 4) input weight, a (4,) hidden bias, a (4, 1) output weight and a (1,) output bias, thirteen scalars in all. Training is 120 compiled calls of a plain gradient step with rate 0.05 on five points of `tanh(2x)`. Each task then checks one property of that pipeline rather than a tuned accuracy target.

**Why it is correct here:** Replay holds because `initialize` derives both weight draws from one key by a fixed split. The gradient tree mirrors the parameter tree leaf for leaf. One eager step and one compiled step consume identical state, batch and rate, so their leaves agree. Width four gives 4 + 4 + 4 + 1 = 13 parameters and width five gives 16, since each hidden unit brings one input weight, one bias and one output weight.

## Exercise 1: Replay initialization

The complete deterministic initialization policy, not only a label called seed, establishes this replay.

**Expected:** Matching tree structure and values.

```python
a = initialize(jax.random.key(31))
b = initialize(jax.random.key(31))
for x, y in zip(jax.tree.leaves(a), jax.tree.leaves(b)):
    close(x, y)
```

**Plausible wrong approach:** Replaying with `jax.random.key(31)` but splitting it in another order, or drawing the output weight first, gives different values under the same seed label. The whole initialization policy must be replayed.

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
assert sum(float(jnp.vdot(x, x)) for x in jax.tree.leaves(g)) > 0.0
```

**Plausible wrong approach:** Asserting that every gradient leaf is nonzero fails here. Inputs and targets are symmetric about zero and the initial network is odd, so the mean residual and the output bias gradient are exactly zero at initialization.

## Exercise 3: Check one compiled update

This is a compilation parity check with the same batch, reduction and learning rate.

**Expected:** Matching updated leaves.

```python
p = initialize(jax.random.key(31))
a, b = step(p, train_x, train_y), compiled_step(p, train_x, train_y)
for x, y in zip(jax.tree.leaves(a), jax.tree.leaves(b)):
    close(x, y)
```

**Plausible wrong approach:** Comparing the eager and compiled paths after unequal step counts, or after training one path, compares two different states. The parity check uses one step from the same initialization.

## Exercise 4: Evaluate untouched inputs

The numerical value is an observation to report, not a threshold tuned on these final points.

**Expected:** A finite nonnegative held-out loss over exactly two targets.

```python
p = train()
value = objective(p, heldout_x, heldout_y)
assert heldout_x.shape[0] == 2
assert bool(jnp.isfinite(value)) and float(value) >= 0.0
```

**Plausible wrong approach:** Choosing an acceptance threshold after looking at the held-out loss turns the two points at -0.75 and 0.75 into tuning data. The lesson reports the value and asserts only that it is finite and nonnegative.

## Exercise 5: Separate training from inference

This model has no stochastic or mutable inference state. A later dropout model needs an explicit mode/key policy.

**Expected:** Matching deterministic predictions; no parameter update.

```python
p = train()
a, b = forward(p, heldout_x), forward(p, heldout_x)
close(a, b)
```

**Plausible wrong approach:** Expecting inference to need a mode switch or key is a habit from dropout models. This network has no stochastic layer, so two forward calls with the same parameters must match exactly.

## Exercise 6: Check an architecture change

Each new hidden unit adds one input weight, one hidden bias and one output weight; the output bias is shared.

**Expected:** Width five would contain 16 parameters, three more than width four.

```python
count = lambda width: width + width + width + 1
assert count(4) == 13 and count(5) == 16
```

**Plausible wrong approach:** Counting four new parameters per hidden unit, including an extra output bias, predicts 17 for width five. The output bias belongs to the single output and is shared, so the count is 16.

## How to verify

Run the reference and confirm `jax-015: 8 asserted cases passed`. Print `jax.tree.map(jnp.shape, initialize(jax.random.key(31)))` and sum the sizes to get 13. Then print the gradient's `b2` leaf at initialization and confirm it is zero, which shows why the reference checks the total gradient norm instead.

## Scope of this evidence

If training does not improve, inspect an exact one-step state, the objective reduction and the gradient tree before adjusting the budget. If held-out results disappoint, report them without retuning on those same points. Do not confuse the fixed synthetic target rule with an empirical population claim.

Port the one-step calculation to an existing framework route with matched initial arrays. Explain what an optimizer package or model library would add, then design a separate validation split before comparing widths or learning rates.
