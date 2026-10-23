# tf-018: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Normalization can introduce state and dependencies between observations. Batch normalization estimates statistics over a training batch and updates moving statistics for later inference. Layer normalization computes statistics across each example's features, so an unrelated example should not alter a row's output. These are different mechanisms even when both produce centered values. Batch normalization's moving mean starts at zero here. With momentum.5 and batch mean[2,4], one update produces[1,2]. Evaluation uses the stored state and should not update it. In sequence models, normalization across time can leak future information; tokenwise feature normalization avoids that particular dependency.

**Moving statistic:** Stored estimate updated during training.

**Batch coupling:** One observation affecting another through shared batch statistics.

**Feature axis:** The dimension reduced independently within each row.

## Reading the implementation

BatchNormalization(momentum=.5) keeps nontrainable moving variables as well as scale and offset parameters. training=True updates the moving mean using momentum*old+(1-momentum)*batch. LayerNormalization(axis=-1) reduces only the trailing feature axis. Its epsilon prevents division by zero and means the normalized variance is approximately, rather than exactly, one.

## Exercise 1: Update moving state

The question is: Apply BatchNorm with momentum.5 to rows[1,3],[3,5].

The batch mean is[2,4], so blending it equally with the initial zero state gives[1,2]. It is not yet the full batch mean.

```python
bn=tf.keras.layers.BatchNormalization(momentum=.5); x=tf.constant([[1.,3.],[3.,5.]])
bn(x,training=True)
np.testing.assert_allclose(bn.moving_mean.numpy(),[1,2],atol=1e-6,rtol=0)
```

**Expected:** moving mean[1,2].

**Verify:** Compare the computed values or written argument with moving mean[1,2].

## Exercise 2: Freeze evaluation state

The question is: Call BatchNorm in evaluation with a very different batch and compare moving means.

The inference call uses learned state rather than adapting to the new observation. Accidental training=True would make predictions depend on evaluation batch composition and mutate the model.

```python
before=bn.moving_mean.numpy().copy(); bn(tf.constant([[100.,200.]]),training=False)
np.testing.assert_array_equal(before,bn.moving_mean.numpy())
```

**Expected:** state remains[1,2].

**Verify:** Compare the computed values or written argument with state remains[1,2].

## Exercise 3: Test row independence

The question is: Apply LayerNorm to one row and to the same row beside[100,200].

Each row computes its own feature mean and variance. The unrelated row has no role in those reductions, providing a direct test of the axis choice.

```python
ln=tf.keras.layers.LayerNormalization(axis=-1)
a=ln(tf.constant([[1.,3.]])).numpy()[0]; b=ln(tf.constant([[1.,3.],[100.,200.]])).numpy()[0]
np.testing.assert_allclose(a,b,atol=1e-6,rtol=0)
```

**Expected:** first row matches within1e-6.

**Verify:** Compare the computed values or written argument with first row matches within1e-6.

## Exercise 4: Expose batch dependence

The question is: Compare raw batch-centered first rows before and after adding an extreme row.

Centering alone already exhibits the coupling; division by variance is not required to expose it. The example isolates one part of BatchNorm with simple arithmetic.

```python
small=np.array([[1.,3.],[3.,5.]]); large=np.vstack([small,[98.,199.]])
np.testing.assert_array_equal(small[0]-small.mean(0),[-1,-1])
np.testing.assert_array_equal(large[0]-large.mean(0),[-33,-66])
```

**Expected:** first row changes from[-1,-1] to[-33,-66].

**Verify:** Compare the computed values or written argument with first row changes from[-1,-1] to[-33,-66].

## Exercise 5: Repeat the state update

The question is: Apply the original batch a second time in training mode.

The second update starts from the stored[1,2], not zero. The history of training batches therefore matters even when all trainable weights are frozen.

```python
bn(x,training=True)
np.testing.assert_allclose(bn.moving_mean.numpy(),[1.5,3],atol=1e-6,rtol=0)
```

**Expected:** moving mean[1.5,3].

**Verify:** Compare the computed values or written argument with moving mean[1.5,3].

## Exercise 6: Handle a constant feature row

The question is: Normalize a row[5,5] with LayerNorm and default zero offset.

A constant row has zero variance. Epsilon avoids division by zero, and the centered numerator is zero. Removing epsilon would turn this valid input into an undefined calculation.

```python
constant=ln(tf.constant([[5.,5.]])).numpy()
assert np.isfinite(constant).all(); np.testing.assert_allclose(constant,[[0,0]],atol=1e-6,rtol=0)
```

**Expected:** finite output[0,0].

**Verify:** Compare the computed values or written argument with finite output[0,0].

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
