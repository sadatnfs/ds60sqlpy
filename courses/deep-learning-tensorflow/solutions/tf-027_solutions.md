# tf-027: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Transfer learning reuses a representation for a related task. Freezing a base means its parameters should not receive optimizer updates while a new head learns from its outputs. The base can still perform computation; frozen does not mean bypassed. Normalization and dropout also have mode-dependent behavior, so a frozen base should be called with a deliberate training flag. Here a small deterministic two-feature transform stands in for the locally trained base from the classifier capstone. No pretrained weights are downloaded. A relabelled target tests whether the new head can change without altering the base. Unfreezing is a new phase with an explicit optimizer policy.

**Base:** The reused representation-producing part of a model.

**Head:** A task-specific output mapping trained on that representation.

**Freeze:** Exclude a parameter set from optimizer updates.

## Reading the implementation

Set base.trainable=False before constructing the training variable list. Use base(x,training=False) to preserve its inference behavior. Train only head.trainable_variables. Snapshot all base weights before the update and compare arrays afterward. When unfreezing, use a new optimizer or explicitly build optimizer state for the newly trainable variables rather than assuming an old optimizer knows them.

## Exercise 1: Construct the local base

The question is: Create a fixed two-feature identity Dense base and freeze it.

The identity fixture keeps transfer semantics visible. In the earlier capstone the base may be learned, but freezing should obey the same state contract.

```python
base = tf.keras.layers.Dense(2, use_bias=False, kernel_initializer=tf.keras.initializers.Identity())
x = tf.constant([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
base(x)
base.trainable = False
np.testing.assert_array_equal(base(x).numpy(), x.numpy())
assert not base.trainable_variables
```

**Expected:** base output equals input; no trainable base variables.

**Verify:** Compare the computed values or written argument with base output equals input; no trainable base variables.

## Exercise 2: Train a new head

The question is: Attach a zero-initialized one-unit head; fit targets[1,2,3] for one SGD step.

Zero initial outputs give nonzero residuals, so this fixture has an observable update. A trainable flag alone would not prove that an optimizer actually changed the head.

```python
head = tf.keras.layers.Dense(1, use_bias=False, kernel_initializer="zeros")
features = base(x, training=False)
head(features)
before = head.get_weights()[0].copy()
target = tf.constant([[1.0], [2.0], [3.0]])
with tf.GradientTape() as tape:
    loss = tf.reduce_mean((head(features) - target) ** 2)
g = tape.gradient(loss, head.trainable_variables)
tf.keras.optimizers.SGD(0.1).apply_gradients(zip(g, head.trainable_variables))
assert not np.array_equal(before, head.get_weights()[0])
```

**Expected:** at least one head coefficient changes.

**Verify:** Compare the computed values or written argument with at least one head coefficient changes.

## Exercise 3: Prove base preservation

The question is: Compare the base kernel with identity after head training.

A weight snapshot provides direct evidence. Checking only that base.trainable is false would miss an accidental explicit assignment outside the optimizer.

```python
np.testing.assert_array_equal(base.get_weights()[0], np.eye(2, dtype="float32"))
```

**Expected:** base weights remain byte-identical to identity.

**Verify:** Compare the computed values or written argument with base weights remain byte-identical to identity.

## Exercise 4: Compare predictions

The question is: Evaluate the new head on all three local records and compare with initial zero predictions.

The head has learned a direction toward the relabelled target. One update does not demonstrate good final fit, and the exercise does not present it as a completed training run.

```python
pred = head(base(x, training=False)).numpy()
assert pred.shape == (3, 1) and (pred > 0).all()
```

**Expected:** all three predictions positive.

**Verify:** Compare the computed values or written argument with all three predictions positive.

## Exercise 5: Begin an explicit unfreeze phase

The question is: Unfreeze the base and initialize a new SGD optimizer; differentiate a combined loss.

The lower rate is declared as part of a new phase, not inferred from a universal transfer rule. A new optimizer avoids silently reusing an incompatible slot-variable set.

```python
base.trainable = True
variables = base.trainable_variables + head.trainable_variables
with tf.GradientTape() as tape:
    loss = tf.reduce_mean((head(base(x, training=False)) - target) ** 2)
grads = tape.gradient(loss, variables)
assert len(grads) == 2 and all(g is not None for g in grads)
tf.keras.optimizers.SGD(0.01).apply_gradients(zip(grads, variables))
```

**Expected:** both base and head now have connected gradients.

**Verify:** Compare the computed values or written argument with both base and head now have connected gradients.

## Exercise 6: Detect changed base state

The question is: Compare the unfrozen base with its original identity after the explicit update.

This control demonstrates that the preservation test is capable of detecting real changes. It helps distinguish successful freezing from a fixture whose gradients were zero everywhere.

```python
assert not np.array_equal(base.get_weights()[0], np.eye(2, dtype="float32"))
```

**Expected:** base is no longer identical.

**Verify:** Compare the computed values or written argument with base is no longer identical.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
