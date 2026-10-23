# tf-011: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Keras packages the same computation that the earlier tape lesson exposed. Dense computes a matrix product and optionally adds a bias. Compile selects the loss and optimizer but does not itself update weights. Training evaluates the forward function, reduces the loss, differentiates and applies the optimizer. To compare a high-level API with the hand-derived update, every relevant choice must match: no intercept, a zero initial weight, mean squared error, full-batch SGD and the same rate. Otherwise a difference may reflect a different model or objective instead of an API bug. Evaluation must be distinguished from a training call because it should not apply gradients.

**Dense:** An affine feature transformation with tracked weights.

**Compile:** Configuration of loss, optimizer and metrics.

**Training call:** Forward, differentiation and update on current weights.

## Reading the implementation

Input(shape=(1,)) excludes the batch dimension. Dense(1,use_bias=False) creates a single trainable scalar kernel. Reshape the three observations to (3,1), matching targets exactly. Compile uses SGD(.1) with loss='mse'. train_on_batch executes one full-batch step without a data-shuffle dependency. get_weights returns NumPy copies useful for comparison. A new model is required for each independent control.

## Exercise 1: Construct a scalar model

The question is: Create a zero-initialized single-unit model without bias and inspect its parameter count.

Excluding a bias preserves the exact scalar model yhat=w*x. A Dense layer with its default bias would introduce a second parameter and a second gradient, invalidating the direct comparison.

```python
model=tf.keras.Sequential([tf.keras.Input(shape=(1,)),tf.keras.layers.Dense(1,use_bias=False,kernel_initializer='zeros')])
x=np.array([[1.],[2.],[3.]],dtype='float32'); y=2*x
assert model.count_params()==1
np.testing.assert_array_equal(model(x).numpy(),np.zeros((3,1)))
```

**Expected:** one parameter and all initial predictions0.

**Verify:** Compare the computed values or written argument with one parameter and all initial predictions0.

## Exercise 2: Audit the first update

The question is: Compile with mean squared error and SGD(.1), then call train_on_batch once.

The API may report the loss used for the update, rather than the loss at the updated weight. Recompute predictions after the step to distinguish before from after.

```python
model.compile(optimizer=tf.keras.optimizers.SGD(.1),loss='mse')
model.train_on_batch(x,y)
np.testing.assert_allclose(model.get_weights()[0],[[28/15]],atol=1e-6,rtol=0)
np.testing.assert_allclose(np.mean((model(x).numpy()-y)**2),56/675,atol=1e-6,rtol=0)
```

**Expected:** kernel28/15 and post-update loss56/675 within1e-6.

**Verify:** Compare the computed values or written argument with kernel28/15 and post-update loss56/675 within1e-6.

## Exercise 3: Inspect forward shape

The question is: Pass two observations [[4],[5]] through the trained model and inspect output axes.

The leading dimension counts observations. Keeping the output column avoids broadcasting a vector target across a batch into a pairwise error matrix.

```python
pred=model(np.array([[4.],[5.]],dtype='float32')).numpy()
assert pred.shape==(2,1)
np.testing.assert_allclose(pred[:,0],[112/15,28/3],atol=1e-6,rtol=0)
```

**Expected:** shape(2,1), predictions112/15 and28/3.

**Verify:** Compare the computed values or written argument with shape(2,1), predictions112/15 and28/3.

## Exercise 4: Evaluation leaves weights alone

The question is: Snapshot the kernel, run a forward evaluation with training=False, and compare.

A forward evaluation can calculate predictions without an optimizer step. More complex layers have training-dependent behavior, which is why explicitly passing the flag becomes important later.

```python
before=model.get_weights()[0].copy(); model(x,training=False)
np.testing.assert_array_equal(before,model.get_weights()[0])
```

**Expected:** kernel is exactly unchanged.

**Verify:** Compare the computed values or written argument with kernel is exactly unchanged.

## Exercise 5: Show the extra intercept

The question is: Construct an otherwise equivalent Dense layer with bias enabled and count trainable scalars.

A zero initial bias still has a gradient. Zero initialization does not freeze a parameter. Removing a parameter and initializing it to zero are different modeling decisions.

```python
with_bias=tf.keras.Sequential([tf.keras.Input(shape=(1,)),tf.keras.layers.Dense(1,kernel_initializer='zeros',bias_initializer='zeros')])
assert with_bias.count_params()==2
np.testing.assert_array_equal(with_bias.get_weights()[1],[0])
```

**Expected:** 2 parameters; bias starts0.

**Verify:** Compare the computed values or written argument with 2 parameters; bias starts0.

## Exercise 6: Compare the scalar oracle

The question is: Compute the first gradient directly from NumPy residuals and inputs, without Keras.

An independent formula guards against using two wrappers around the same broken calculation. The float32 tolerance reflects arithmetic precision and does not excuse a mismatched target shape.

```python
grad=2*np.mean((0*x-y)*x)
np.testing.assert_allclose(grad,-56/3,atol=1e-6,rtol=0)
np.testing.assert_allclose(-.1*grad,28/15,atol=1e-6,rtol=0)
```

**Expected:** gradient-56/3 and update28/15.

**Verify:** Compare the computed values or written argument with gradient-56/3 and update28/15.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
