# tf-026: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A custom layer separates construction of persistent parameters from repeated evaluation. Creating a new weight in every call would change the model whenever it sees another batch. Keras tracks weights created through add_weight, typically in build once the feature width is known. A residual connection adds an input to a transformed version of itself. Both operands must have compatible shapes; a projection is required if feature widths differ. This lesson uses a square linear residual with zero initial kernel, so its initial behavior is exactly the identity. The transparent starting function makes tracked-state and gradient tests easy to interpret.

**Tracked variable:** Persistent model state registered with the layer.

**Residual:** An input added to a transformation with matching dimensions.

**Build:** One-time creation of weights for a declared input shape.

## Reading the implementation

build(input_shape) reads the trailing feature width and creates one square kernel. call(x) computes x+x@kernel. The same layer object reuses that kernel on later calls. trainable_variables supplies the variables the optimizer should update. A width mismatch should be reported rather than silently constructing a new parameter set. Batch length may change without changing feature width.

## Exercise 1: Create an identity residual

The question is: Call a width2 residual with zero kernel on[[1,2],[3,4]].

The zero branch contributes nothing initially. This is a useful reference behavior but does not mean the branch has no gradient or will remain zero during training.

```python
layer=Residual(); x=tf.constant([[1.,2.],[3.,4.]]); out=layer(x)
np.testing.assert_array_equal(out.numpy(),x.numpy()); assert len(layer.trainable_variables)==1
```

**Expected:** output equals input; one tracked kernel.

**Verify:** Compare the computed values or written argument with output equals input; one tracked kernel.

## Exercise 2: Reuse the state

The question is: Call the layer on another batch of the same width and compare variable object identity.

A new batch should change transient activations, not create a new model. Object identity complements a parameter count, since replacing one variable with another could preserve the count.

```python
variable=layer.trainable_variables[0]; layer(tf.constant([[9.,8.]]))
assert layer.trainable_variables[0] is variable and len(layer.trainable_variables)==1
```

**Expected:** same variable object and variable count1.

**Verify:** Compare the computed values or written argument with same variable object and variable count1.

## Exercise 3: Assign a known transform

The question is: Set the kernel to identity and inspect the residual output.

The branch now reproduces the input, and the residual adds the original input again. The exact doubling exposes the addition instead of relying on random weights.

```python
layer.kernel.assign(tf.eye(2)); np.testing.assert_array_equal(layer(x).numpy(),2*x.numpy())
```

**Expected:** output2*x.

**Verify:** Compare the computed values or written argument with output2*x.

## Exercise 4: Reject an incompatible width

The question is: Call the built width2 layer with a width3 input.

A residual addition cannot repair a mismatched matrix product. Supporting a new feature width requires a separately designed projection or layer instance.

```python
try: layer(tf.ones((1,3)))
except ValueError: pass
else: raise AssertionError('width mismatch accepted')
```

**Expected:** ValueError naming feature width.

**Verify:** Compare the computed values or written argument with ValueError naming feature width.

## Exercise 5: Check branch gradients

The question is: Differentiate the sum of output entries with respect to the kernel.

Each output column sees the same sum of input features under a sum objective. The identity skip path adds no kernel derivative, while the learned branch remains connected.

```python
with tf.GradientTape() as tape: total=tf.reduce_sum(layer(x))
g=tape.gradient(total,layer.kernel)
np.testing.assert_array_equal(g.numpy(),[[4,4],[6,6]])
```

**Expected:** gradient matrix[[4,4],[6,6]].

**Verify:** Compare the computed values or written argument with gradient matrix[[4,4],[6,6]].

## Exercise 6: Count parameters by width

The question is: Build a separate width3 layer and count its square kernel entries.

Parameter growth is quadratic in this dense branch width. Batch size does not contribute to the count because the same kernel is shared across observations.

```python
other=Residual(); other(tf.ones((1,3)))
assert other.count_params()==9 and layer.count_params()==4
```

**Expected:** 9 parameters; width2 layer remains4.

**Verify:** Compare the computed values or written argument with 9 parameters; width2 layer remains4.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
