# tf-013: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A binary logit is an unrestricted score whose sigmoid is a probability under the chosen model. It is not already a probability. Binary cross entropy compares that probability with a zero-or-one target. A logits-aware implementation combines the sigmoid and logarithms into a stable calculation. The decision threshold is a separate policy: moving it changes predicted classes without changing the fitted scores. This distinction matters when false positives and false negatives have different costs. The three-point fixture is designed to make the boundary at probability one half explicit. It cannot show that the probabilities are calibrated on real observations.

**Logit:** An unrestricted binary score before the sigmoid transformation.

**Threshold:** A probability boundary used to choose a class.

**Binary cross entropy:** Negative log probability assigned to the observed binary label.

## Reading the implementation

tf.math.sigmoid converts each score independently. sigmoid_cross_entropy_with_logits requires labels and logits of equal shape and computes a loss per entry. reduce_mean chooses the example denominator. Compare probability>=threshold for a declared tie policy. Do not apply sigmoid twice or feed a probability to a function that expects a logit; both can produce finite but incorrectly interpreted losses.

## Exercise 1: Convert scores

The question is: Convert logits[-2,0,2] into probabilities and inspect the central value.

The sigmoid is monotonic, so ordering survives. A score of zero lies at the probability midpoint, which makes it a useful exact boundary fixture.

```python
z=tf.constant([-2.,0.,2.]); p=tf.math.sigmoid(z).numpy()
assert p[1]==.5 and np.all(np.diff(p)>0)
```

**Expected:** middle probability.5; probabilities increase.

**Verify:** Compare the computed values or written argument with middle probability.5; probabilities increase.

## Exercise 2: Check the midpoint loss

The question is: Calculate positive-label binary cross entropy at zero logit.

A fifty-fifty prediction assigns probability one half to either outcome. Its negative logarithm provides an independent reference that does not depend on a trained model.

```python
loss=tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant([1.]),logits=tf.constant([0.]))
np.testing.assert_allclose(loss.numpy(),[np.log(2)],atol=1e-6,rtol=0)
```

**Expected:** loss log(2) within1e-6.

**Verify:** Compare the computed values or written argument with loss log(2) within1e-6.

## Exercise 3: Move the threshold

The question is: Compare decisions at thresholds.5 and.8 with >= ties.

Only the middle decision changes. Save scores independently from decisions so threshold exploration does not look like a second model fitting operation.

```python
assert (p>=.5).tolist()==[False,True,True]
assert (p>=.8).tolist()==[False,False,True]
```

**Expected:** decisions[False,True,True] versus[False,False,True].

**Verify:** Compare the computed values or written argument with decisions[False,True,True] versus[False,False,True].

## Exercise 4: Expose a convention mismatch

The question is: Treat probability.5 as if it were a logit and compare the positive-label loss with log2.

The mistaken argument is interpreted as a score favoring the positive class. The API cannot infer that the caller intended a probability; explicit naming and shape contracts are necessary.

```python
wrong=float(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant(1.),logits=tf.constant(.5)))
assert abs(wrong-np.log(2))>.1
```

**Expected:** wrong loss differs from log2 by more than.1.

**Verify:** Compare the computed values or written argument with wrong loss differs from log2 by more than.1.

## Exercise 5: Stress large scores

The question is: Calculate losses for logits1000,-1000 with labels1,0 using the logits-aware form.

A naive log(sigmoid()) path can lose precision at extreme probabilities. The stable form handles the algebra before exponentiation creates overflow or logarithms receive rounded zero.

```python
stable=tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant([1.,0.]),logits=tf.constant([1000.,-1000.])).numpy()
assert np.isfinite(stable).all(); np.testing.assert_allclose(stable,[0,0],atol=1e-6,rtol=0)
```

**Expected:** both finite losses approximately0.

**Verify:** Compare the computed values or written argument with both finite losses approximately0.

## Exercise 6: Count decisions separately

The question is: For labels[0,1,1], count errors under the two thresholds.

This count is a decision metric. It does not replace the probability loss and cannot show that threshold .5 is optimal for a different cost structure or population.

```python
labels=np.array([0,1,1]); assert np.count_nonzero((p>=.5)!=labels)==0
assert np.count_nonzero((p>=.8)!=labels)==1
```

**Expected:** 0 errors at.5 and1 at.8 on this fixture.

**Verify:** Compare the computed values or written argument with 0 errors at.5 and1 at.8 on this fixture.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
