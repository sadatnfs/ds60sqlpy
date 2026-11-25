# tf-026: explanatory solutions

Open these answers after an attempt; they reuse the guide's inputs ([comparison steps](../STUDY-GUIDE.md#after-the-solutions)).

## Mechanism review

A custom layer separates construction of persistent parameters from repeated evaluation. Creating a new weight in every call would change the model whenever it sees another batch. Keras tracks weights created through add_weight, typically in build once the feature width is known. A residual connection adds an input to a transformed version of itself. Both operands must have compatible shapes; a projection is required if feature widths differ. This lesson uses a square linear residual with zero initial kernel, so its initial behavior is exactly the identity. The transparent starting function makes tracked-state and gradient tests easy to interpret.

**Tracked variable:** Persistent model state registered with the layer.

**Residual:** An input added to a transformation with matching dimensions.

**Build:** One-time creation of weights for a declared input shape.

## Reading the implementation

build(input_shape) reads the trailing feature width and creates one square kernel. call(x) computes x+x@kernel. The same layer object reuses that kernel on later calls. trainable_variables supplies the variables the optimizer should update. A width mismatch should be reported rather than silently constructing a new parameter set. Batch length may change without changing feature width.

## Exercise 1: Create an identity residual

The question is: Call a width 2 residual with zero kernel on [[1, 2], [3, 4]].

The zero branch contributes nothing initially. This is a useful reference behavior but does not mean the branch has no gradient or will remain zero during training.

```python
layer = Residual()
x = tf.constant([[1.0, 2.0], [3.0, 4.0]])
out = layer(x)
np.testing.assert_array_equal(out.numpy(), x.numpy())
assert len(layer.trainable_variables) == 1
```

**Expected:** output equals input; one tracked kernel.

**Verify:** In a fresh process, the exercise checks confirm `out.numpy()` equals `x.numpy()` and `len(layer.trainable_variables) == 1`.

## Exercise 2: Reuse the state

The question is: Call the layer on another batch of the same width and compare variable object identity.

A new batch should change transient activations, not create a new model. Object identity complements a parameter count, since replacing one variable with another could preserve the count.

```python
variable = layer.trainable_variables[0]
layer(tf.constant([[9.0, 8.0]]))
assert layer.trainable_variables[0] is variable and len(layer.trainable_variables) == 1
```

**Expected:** same variable object and variable count 1.

**Verify:** In a fresh process, the exercise checks confirm `layer.trainable_variables[0] is variable` and `len(layer.trainable_variables) == 1`.

## Exercise 3: Assign a known transform

The question is: Set the kernel to identity and inspect the residual output.

The branch now reproduces the input, and the residual adds the original input again. The exact doubling exposes the addition instead of relying on random weights.

```python
layer.kernel.assign(tf.eye(2))
np.testing.assert_array_equal(layer(x).numpy(), 2 * x.numpy())
```

**Expected:** output 2*x.

**Verify:** In a fresh process, the exercise checks confirm `layer(x).numpy()` equals `2 * x.numpy()`.

## Exercise 4: Reject an incompatible width

The question is: Call the built width 2 layer with a width 3 input.

A residual addition cannot repair a mismatched matrix product. Supporting a new feature width requires a separately designed projection or layer instance.

```python
try:
    layer(tf.ones((1, 3)))
except ValueError:
    pass
else:
    raise AssertionError("width mismatch accepted")
```

**Expected:** ValueError naming feature width.

**Verify:** In a fresh process, the exercise checks confirm `layer(tf.ones((1, 3)))` raises `ValueError`.

## Exercise 5: Check branch gradients

The question is: Differentiate the sum of output entries with respect to the kernel.

Each output column sees the same sum of input features under a sum objective. The identity skip path adds no kernel derivative, while the learned branch remains connected.

```python
with tf.GradientTape() as tape:
    total = tf.reduce_sum(layer(x))
g = tape.gradient(total, layer.kernel)
np.testing.assert_array_equal(g.numpy(), [[4, 4], [6, 6]])
```

**Expected:** gradient matrix [[4, 4], [6, 6]].

**Verify:** In a fresh process, the exercise checks confirm `g.numpy()` equals `[[4, 4], [6, 6]]`.

## Exercise 6: Count parameters by width

The question is: Build a separate width 3 layer and count its square kernel entries.

Parameter growth is quadratic in this dense branch width. Batch size does not contribute to the count because the same kernel is shared across observations.

```python
other = Residual()
other(tf.ones((1, 3)))
assert other.count_params() == 9 and layer.count_params() == 4
```

**Expected:** 9 parameters; width 2 layer remains 4.

**Verify:** In a fresh process, the exercise checks confirm `other.count_params() == 9` and `layer.count_params() == 4`.

