# tf-017: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Regularization changes the training objective or the training computation. An L1 penalty sums absolute weights; an L2 penalty here sums squared weights, with its coefficient declared separately. These quantities differ from data loss and have different scaling. Dropout randomly removes activations during training while rescaling retained values; evaluation normally uses the unmodified activations. A random training call should be tested through invariants such as allowed output values and shape, not a hardcoded random bit pattern across platforms. Evaluation behavior should be deterministic for this isolated layer. None of these mechanisms automatically proves improved generalization.

**Penalty:** A parameter-dependent term added to an objective.

**Dropout:** A stochastic training transformation that zeroes activations.

**Evaluation mode:** Inference behavior with training-time stochastic changes disabled.

## Reading the implementation

reduce_sum(abs(w)) and reduce_sum(square(w)) implement the declared penalty conventions. Add lambda*penalty to data loss only when that is the intended objective. Dropout(rate=.5) with training=True maps each unit input to0 or2. training=False returns the input. Keras regularizer conventions and optimizer weight decay should be checked explicitly instead of being assumed interchangeable.

## Exercise 1: Calculate penalties

The question is: Compute L1 and squared L2 sums for weights[1,-2].

The name L2 can mean a norm or a squared penalty in different contexts. This exercise explicitly uses the sum of squares, avoiding an unexplained square root or half factor.

```python
w=tf.constant([1.,-2.]); l1=float(tf.reduce_sum(tf.abs(w))); l2=float(tf.reduce_sum(w*w))
assert (l1,l2)==(3.,5.)
```

**Expected:** L1=3; squaredL2=5.

**Verify:** Compare the computed values or written argument with L1=3; squaredL2=5.

## Exercise 2: Switch dropout to evaluation

The question is: Apply dropout.5 twice to ones with training=False.

Evaluation removes the random masking behavior. Testing repeated calls establishes this local contract without making claims about other random components in a full pipeline.

```python
layer=tf.keras.layers.Dropout(.5); x=tf.ones((4,8)); a=layer(x,training=False); b=layer(x,training=False)
np.testing.assert_array_equal(a.numpy(),x.numpy()); np.testing.assert_array_equal(b.numpy(),x.numpy())
```

**Expected:** both outputs equal the input.

**Verify:** Compare the computed values or written argument with both outputs equal the input.

## Exercise 3: Inspect training invariants

The question is: Call the same dropout layer with training=True and examine allowed output values.

The retained activations are scaled to keep their expectation unchanged. A finite fixture may coincidentally keep or drop many values; requiring an exact mask would overconstrain the test.

```python
train=layer(x,training=True).numpy()
assert train.shape==(4,8) and set(np.unique(train))<={0.,2.}
```

**Expected:** shape(4,8), values only0 or2.

**Verify:** Compare the computed values or written argument with shape(4,8), values only0 or2.

## Exercise 4: Separate objective terms

The question is: Combine data loss2 with coefficient.1 times squaredL2 and report both components.

Logging only the total makes it hard to distinguish predictive error from a changing regularization cost. The coefficient is part of the objective definition.

```python
data_loss=2.; coefficient=.1; penalty=coefficient*l2
assert penalty==.5 and data_loss+penalty==2.5
```

**Expected:** data2, penalty.5, total2.5.

**Verify:** Compare the computed values or written argument with data2, penalty.5, total2.5.

## Exercise 5: Differentiate the penalty

The question is: Differentiate.1*sum(w²) at[1,-2].

The derivative is2*lambda*w under the stated convention. A half-scaled penalty would have a different gradient, so a coefficient cannot be copied blindly between definitions.

```python
v=tf.Variable([1.,-2.])
with tf.GradientTape() as tape: penalty=.1*tf.reduce_sum(v*v)
np.testing.assert_allclose(tape.gradient(penalty,v).numpy(),[.2,-.4],atol=1e-6,rtol=0)
```

**Expected:** gradient[.2,-.4].

**Verify:** Compare the computed values or written argument with gradient[.2,-.4].

## Exercise 6: Scale weights deliberately

The question is: Double both weights and compare the new penalties with the original values.

The different scaling explains why the penalties discourage large coefficients differently. This arithmetic does not establish which choice will work better on an unseen dataset.

```python
assert float(tf.reduce_sum(tf.abs(2*w)))==6
assert float(tf.reduce_sum((2*w)**2))==20
```

**Expected:** L1 doubles to6; squaredL2 quadruples to20.

**Verify:** Compare the computed values or written argument with L1 doubles to6; squaredL2 quadruples to20.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
