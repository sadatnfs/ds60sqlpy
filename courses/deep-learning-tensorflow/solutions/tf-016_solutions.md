# tf-016: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Stacking affine layers without an intervening nonlinearity still produces an affine function. XOR asks for opposite labels at the diagonally opposite corners of a square, a pattern one affine threshold cannot separate. Two rectified differences create the needed representation: \(h_{1}=\max(x_{1}-x_{2},0)\), \(h_{2}=\max(x_{2}-x_{1},0)\). Their sum is one exactly when the inputs differ. This hand-built network separates representational capacity from optimization. If the construction works but a fitted model does not, the architecture may be capable while the training procedure failed. Initialization changes the starting state and symmetry of fitting; it cannot repair an architecture that lacks the required function.

**Nonlinearity:** A transformation that cannot be represented by a single affine map.

**ReLU:** The rectified linear function max(z,0).

**Capacity:** The set of functions a model architecture can represent.

## Reading the implementation

A Dense transform computes X@W. The chosen columns of W form x1-x2 and x2-x1. ReLU applies max(z,0) independently, then reduce_sum combines the hidden units. Before fitting, evaluate all four binary inputs. The affine contradiction comes from summing inequalities at the two positive and two negative corners, so it does not depend on testing many random initializations.

## Exercise 1: Construct XOR

The question is: Evaluate two rectified differences on inputs(0,0),(0,1),(1,0),(1,1).

The hidden features encode the two possible directions of disagreement. Their values are never simultaneously positive on the binary fixture, so their sum behaves like XOR.

```python
x = tf.constant([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
w = tf.constant([[1.0, -1.0], [-1.0, 1.0]])
h = tf.nn.relu(x @ w)
output = tf.reduce_sum(h, axis=1)
np.testing.assert_array_equal(output.numpy(), [0, 1, 1, 0])
```

**Expected:** outputs[0,1,1,0].

**Verify:** Compare the computed values or written argument with outputs[0,1,1,0].

## Exercise 2: Remove the nonlinearity

The question is: Sum the two raw difference columns before applying a threshold.

The columns cancel exactly. The ReLU was the step that prevented the positive and negative differences from cancelling, rather than merely adding an extra layer name.

```python
np.testing.assert_array_equal(tf.reduce_sum(x @ w, axis=1).numpy(), [0, 0, 0, 0])
```

**Expected:** all four sums0.

**Verify:** Compare the computed values or written argument with all four sums0.

## Exercise 3: Compose affine matrices

The question is: Multiply two fixed matrices and verify that a two-layer linear computation equals one matrix product.

Associativity collapses linear layers. Bias terms can also be combined, so adding affine depth alone does not overcome the XOR separation problem.

```python
a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
b = tf.constant([[2.0], [-1.0]])
np.testing.assert_allclose(((x @ a) @ b).numpy(), (x @ (a @ b)).numpy(), atol=1e-6, rtol=0)
```

**Expected:** two paths agree within 1e-6.

**Verify:** Compare the computed values or written argument with two paths agree within 1e-6.

## Exercise 4: Inspect a dead region

The question is: Evaluate ReLU and its tape gradient at-2 and+2.

A negative preactivation has zero local derivative in this example. Units initialized or driven into inactive regions can receive no update from those observations, which is distinct from a missing gradient path.

```python
z = tf.Variable([-2.0, 2.0])
with tf.GradientTape() as tape:
    total = tf.reduce_sum(tf.nn.relu(z))
np.testing.assert_array_equal(tf.nn.relu(z).numpy(), [0, 2])
np.testing.assert_array_equal(tape.gradient(total, z).numpy(), [0, 1])
```

**Expected:** values[0,2], gradients[0,1].

**Verify:** Compare the computed values or written argument with values[0,2], gradients[0,1].

## Exercise 5: Show symmetry

The question is: Create two hidden units with identical columns and compare their activations on every XOR input.

Identical initialization can leave units redundant under symmetric gradient updates. Distinct parameters do not automatically create distinct learned features.

```python
same = tf.constant([[1.0, 1.0], [2.0, 2.0]])
features = tf.nn.relu(x @ same).numpy()
np.testing.assert_array_equal(features[:, 0], features[:, 1])
```

**Expected:** hidden columns match exactly.

**Verify:** Compare the computed values or written argument with hidden columns match exactly.

## Exercise 6: Transfer outside the corners

The question is: Evaluate the fixed construction at(.2,.8) and(.8,.2), and state what it computes away from binary inputs.

The exact network computes absolute difference on continuous inputs. Calling it XOR outside the binary domain would conceal an assumption about the input space.

```python
q = tf.constant([[0.2, 0.8], [0.8, 0.2]])
np.testing.assert_allclose(
    tf.reduce_sum(tf.nn.relu(q @ w), axis=1).numpy(), [0.6, 0.6], atol=1e-6, rtol=0
)
```

**Expected:** both outputs.6; function is absolute difference.

**Verify:** Compare the computed values or written argument with both outputs.6; function is absolute difference.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
