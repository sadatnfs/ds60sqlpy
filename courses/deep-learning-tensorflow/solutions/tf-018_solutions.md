# tf-018: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Normalization has three distinct contracts: which values share statistics, which state changes during training, and which affine parameters are learned. BatchNorm and LayerNorm can use similar arithmetic while differing on all three. A layer name or an axis number is not enough to infer the dependency structure.

For BatchNormalization(axis=-1) on input [N,C], the final axis identifies separate channels whose statistics are retained. The reduction happens over the other axis N. On channels-last images [N,H,W,C], separate channel statistics reduce over N,H,W. In contrast, LayerNormalization(axis=-1) reduces the final feature axis itself. On [N,T,D] it computes a distinct mean and variance for every [N,T] token, reducing D and preserving the token positions. These opposite roles for the axis argument are a common source of plausible-looking but incorrect comparisons.

BatchNorm uses current-batch statistics during a training call and updates moving statistics for later inference. Its scale gamma and offset beta are trainable parameters, while moving mean and variance are nontrainable state updated by the layer. Inference uses the stored state and should not update it. LayerNorm uses the current row's feature statistics in both ordinary training and inference, without maintaining running batch statistics. Its learned affine parameters still matter.

The main fixture keeps the familiar Keras momentum 0.5 example, then adds momentum 0.8 so the update convention becomes visible. Keras momentum is the retention weight of the old statistic. PyTorch BatchNorm momentum is the weight of the new statistic. Equal numerical arguments usually describe different updates; the value 0.5 happens to hide that distinction. Matching moving means alone also does not establish full cross-framework parity, because epsilon, variance-state conventions, layout and mode behavior must be matched explicitly.

**Channel axis:** For BatchNorm, the dimension whose distinct channel statistics are retained while other axes are reduced.

**Reduction axis:** A dimension whose values are combined to compute a statistic; LayerNorm axis=-1 reduces the feature dimension.

**Moving statistics:** Nontrainable state accumulated across training calls and used during BatchNorm inference.

**Affine parameters:** Learned scale gamma and offset beta applied after normalization.

**Momentum convention:** The meaning of the coefficient in a moving-statistic update, which differs between Keras and PyTorch.

## Reading the implementation

### Reduction axes and statistic shapes

| Layer and input | Axis argument means | Reduction axes | Statistic shape before broadcasting |
| --- | --- | --- | --- |
| BatchNorm on [N,C] | retain C distinct channels | N | [C] |
| BatchNorm on [N,H,W,C] | retain C distinct channels | N,H,W | [C] |
| LayerNorm on [N,T,D] | reduce D features | D | [N,T,1] |
| LayerNorm on [N,H,W,C] with axis=-1 | reduce channels at each location | C | [N,H,W,1] |

The last row is not whole-image normalization. Likewise, PyTorch's common channels-first convolution layout requires its own axis reasoning. Translate tensor layout before comparing framework calls. A statistical reduction can preserve the final output shape while changing which observations influence one another.

### Calculate current and moving statistics

For batch [[1,3],[3,5]], the per-channel mean is [2,4]. Each channel has centered values [-1,1] and population variance 1. With initial moving mean [0,0] and Keras momentum m=0.5, the update m*old+(1-m)*batch gives [1,2]. A second identical batch gives [1.5,3]. With a constant batch mean and zero initial mean, the value after t updates is (1-m^t) times that batch mean. Early inference statistics still reflect their initialization.

The initial moving variance is one. The main batch's variance is also one, so that state would not visibly change. A separate probe [[0,0],[4,4]] has population variance four per channel. The Keras update with m=0.5 gives 0.5*1+0.5*4=2.5. PyTorch's documented running-variance update uses the unbiased batch estimate, which is eight for those two observations, so matching its new-batch weight to 0.5 gives 4.5 instead. The TensorFlow fixture executes the Keras result; the paired PyTorch chapter separately exercises that framework's state convention.

### Training output is not inference output

With gamma=1, beta=0 and explicit epsilon=0.001, the training output of the main batch is [[-1,-1],[1,1]]/sqrt(1.001). After one moving-state update, inference instead subtracts [1,2] and divides by sqrt(1.001), giving [[0,1],[2,3]]/sqrt(1.001). It need not be centered on the new inference batch. Using inference mode on unrepresentative or barely initialized state can therefore produce a different result even when no trainable weight changed.

LayerNorm on row [1,3] uses row mean 2 and variance 1. Appending [100,200] as another row does not change those statistics. Learned gamma/beta are omitted from this hand arithmetic by using their default initial values. After affine parameters are learned, the final output need not retain zero mean even though the normalized internal values are centered.

## Exercise 1: Update and inspect moving state

The question is: Apply Keras BatchNorm with momentum 0.5 to [[1,3],[3,5]], then use a separate variance-four probe.

The mean update reveals old-versus-new weighting. The separate variance probe is necessary because a batch variance equal to the initial moving variance would hide whether an update occurred. The output expectation uses current-batch statistics, not the newly updated moving mean.

```python
epsilon = 1e-3
values = tf.constant([[1., 3.], [3., 5.]])
bn = tf.keras.layers.BatchNormalization(axis=-1, momentum=0.5, epsilon=epsilon)
training_output = bn(values, training=True)
np.testing.assert_allclose(bn.moving_mean.numpy(), [1, 2], atol=1e-6, rtol=0)
np.testing.assert_allclose(bn.moving_variance.numpy(), [1, 1], atol=1e-6, rtol=0)
expected = np.array([[-1., -1.], [1., 1.]]) / np.sqrt(1 + epsilon)
np.testing.assert_allclose(training_output.numpy(), expected, atol=1e-6, rtol=0)
probe = tf.keras.layers.BatchNormalization(axis=-1, momentum=0.5, epsilon=epsilon)
probe(tf.constant([[0., 0.], [4., 4.]]), training=True)
np.testing.assert_allclose(probe.moving_variance.numpy(), [2.5, 2.5], atol=1e-6, rtol=0)
```

**Expected:** moving mean [1,2]; main variance stays [1,1]; variance-four probe updates moving variance to [2.5,2.5].

**Verify:** Compare the computed values or written argument with moving mean [1,2]; main variance stays [1,1]; variance-four probe updates moving variance to [2.5,2.5].

## Exercise 2: Freeze evaluation state

The question is: After one training call, evaluate the same batch and compare with the stored-statistic formula.

Inference can change the function's output while leaving all state untouched, because it chooses stored statistics instead of current-batch statistics. State equality and output equality are different checks.

```python
epsilon = 1e-3
values = tf.constant([[1., 3.], [3., 5.]])
bn = tf.keras.layers.BatchNormalization(momentum=0.5, epsilon=epsilon)
training_output = bn(values, training=True).numpy()
mean_before = bn.moving_mean.numpy().copy()
variance_before = bn.moving_variance.numpy().copy()
evaluation = bn(values, training=False).numpy()
expected = (values.numpy() - mean_before) / np.sqrt(variance_before + epsilon)
np.testing.assert_allclose(evaluation, expected, atol=1e-6, rtol=0)
np.testing.assert_array_equal(bn.moving_mean.numpy(), mean_before)
np.testing.assert_array_equal(bn.moving_variance.numpy(), variance_before)
assert not np.allclose(evaluation, training_output)
```

**Expected:** moving state stays unchanged; inference output uses mean [1,2] and differs from training output.

**Verify:** Compare the computed values or written argument with moving state stays unchanged; inference output uses mean [1,2] and differs from training output.

## Exercise 3: Test LayerNorm row independence

The question is: Normalize [1,3] alone and as the first row beside [100,200].

The reduced feature axis belongs to one row. No statistic from the unrelated second row enters the first output. This property depends on the selected axes, not merely on the LayerNorm name.

```python
ln = tf.keras.layers.LayerNormalization(axis=-1, epsilon=1e-3)
alone = ln(tf.constant([[1., 3.]])).numpy()[0]
together = ln(tf.constant([[1., 3.], [100., 200.]])).numpy()[0]
np.testing.assert_allclose(alone, together, atol=1e-6, rtol=0)
np.testing.assert_allclose(alone, np.array([-1., 1.]) / np.sqrt(1.001), atol=1e-6, rtol=0)
assert len(ln.non_trainable_variables) == 0
```

**Expected:** the first output is unchanged; LayerNorm has no running-statistic variables.

**Verify:** Compare the computed values or written argument with the first output is unchanged; LayerNorm has no running-statistic variables.

## Exercise 4: Expose actual BatchNorm batch dependence

The question is: Compare the first row of training normalization with and without the added row [98,199].

The current training batch is part of the BatchNorm function. A record's output can change when its neighbors change, even before considering moving state. The independent NumPy oracle checks the reduction axes and population-variance arithmetic.

```python
small = np.array([[1., 3.], [3., 5.]], dtype=np.float32)
large = np.vstack([small, [98., 199.]]).astype(np.float32)
outputs = []
for batch in [small, large]:
    layer = tf.keras.layers.BatchNormalization(momentum=0.5, epsilon=1e-3)
    observed = layer(tf.constant(batch), training=True).numpy()
    expected = (batch - batch.mean(axis=0, keepdims=True)) / np.sqrt(batch.var(axis=0, keepdims=True) + 1e-3)
    np.testing.assert_allclose(observed, expected, atol=1e-6, rtol=0)
    outputs.append(observed[0])
assert not np.allclose(outputs[0], outputs[1])
np.testing.assert_array_equal(large[0] - large.mean(axis=0), [-33, -66])
```

**Expected:** the output changes and matches independent per-channel NumPy mean/variance calculations.

**Verify:** Compare the computed values or written argument with the output changes and matches independent per-channel NumPy mean/variance calculations.

## Exercise 5: Repeat updates and translate asymmetric momentum

The question is: Repeat the 0.5 update, then run a fresh Keras layer with momentum 0.8 and compare old/new-weight arithmetic.

At 0.5 the coefficients are equal, hiding the convention difference. The asymmetric example identifies which coefficient belongs to the new batch. The Torch values here are an arithmetic comparison from its documented formula, not a claim that a Torch layer ran inside the TensorFlow profile.

```python
values = tf.constant([[1., 3.], [3., 5.]])
bn = tf.keras.layers.BatchNormalization(momentum=0.5)
bn(values, training=True)
bn(values, training=True)
np.testing.assert_allclose(bn.moving_mean.numpy(), [1.5, 3], atol=1e-6, rtol=0)
asymmetric = tf.keras.layers.BatchNormalization(momentum=0.8)
asymmetric(values, training=True)
np.testing.assert_allclose(asymmetric.moving_mean.numpy(), [0.4, 0.8], atol=1e-6, rtol=0)
asymmetric(values, training=True)
np.testing.assert_allclose(asymmetric.moving_mean.numpy(), [0.72, 1.44], atol=1e-6, rtol=0)
batch_mean = np.array([2., 4.])
keras_first = (1 - 0.8) * batch_mean
torch_same_number_formula = 0.8 * batch_mean
torch_matched_formula = 0.2 * batch_mean
assert not np.allclose(keras_first, torch_same_number_formula)
np.testing.assert_allclose(keras_first, torch_matched_formula, atol=1e-12, rtol=0)
```

**Expected:** 0.5 repeat gives [1.5,3]; Keras0.8 first/second means are [0.4,0.8] and [0.72,1.44]; matching Torch new-batch weight is 0.2.

**Verify:** Compare the computed values or written argument with 0.5 repeat gives [1.5,3]; Keras0.8 first/second means are [0.4,0.8] and [0.72,1.44]; matching Torch new-batch weight is 0.2.

## Exercise 6: Handle constant rows and frozen BatchNorm

The question is: Normalize a constant row, then freeze a trained Keras BatchNorm layer and call it with training=True.

Positive epsilon handles a zero-variance row. Keras BatchNorm also has a documented special relationship between trainable=False and inference behavior. This must not be generalized to every layer or copied to PyTorch parameter requires_grad flags, which are separate from module train/eval mode.

```python
ln = tf.keras.layers.LayerNormalization(axis=-1, epsilon=1e-3)
constant = ln(tf.constant([[5., 5.]])).numpy()
assert np.isfinite(constant).all()
np.testing.assert_allclose(constant, [[0, 0]], atol=1e-6, rtol=0)
bn = tf.keras.layers.BatchNormalization(momentum=0.5, epsilon=1e-3)
bn(tf.constant([[1., 3.], [3., 5.]]), training=True)
bn.trainable = False
before_mean = bn.moving_mean.numpy().copy()
before_variance = bn.moving_variance.numpy().copy()
probe = tf.constant([[100., 200.]])
output = bn(probe, training=True).numpy()
np.testing.assert_array_equal(bn.moving_mean.numpy(), before_mean)
np.testing.assert_array_equal(bn.moving_variance.numpy(), before_variance)
expected = (probe.numpy() - before_mean) / np.sqrt(before_variance + 1e-3)
np.testing.assert_allclose(output, expected, atol=2e-5, rtol=0)
```

**Expected:** LayerNorm returns finite zeros; frozen Keras BatchNorm preserves moving state and uses its inference statistics.

**Verify:** Compare the computed values or written argument with LayerNorm returns finite zeros; frozen Keras BatchNorm preserves moving state and uses its inference statistics.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
