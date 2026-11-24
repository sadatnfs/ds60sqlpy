# tf-013: explanatory solutions

Open these answers for Binary logits, probabilities and thresholds after your own attempt at Example A, Convert scores, or after an explicit reveal. Each answer reuses the guide's literal inputs, so a mismatch points to one step. The companion script runs the assertions; this page explains why they test Logit, Threshold, Binary cross entropy. After matching exercise 6, Count decisions separately, invent a new input without looking here.

## Mechanism review

A binary logit is an unrestricted score whose sigmoid is a probability under the chosen model. It is not already a probability. Binary cross entropy compares that probability with a zero-or-one target. A logits-aware implementation combines the sigmoid and logarithms into a stable calculation. The decision threshold is a separate policy: moving it changes predicted classes without changing the fitted scores. This distinction matters when false positives and false negatives have different costs. The three-point fixture is designed to make the boundary at probability one half explicit. It cannot show that the probabilities are calibrated on real observations.

**Logit:** An unrestricted binary score before the sigmoid transformation.

**Threshold:** A probability boundary used to choose a class.

**Binary cross entropy:** Negative log probability assigned to the observed binary label.

## Reading the implementation

`tf.math.sigmoid` converts each score independently. `sigmoid_cross_entropy_with_logits` requires labels and logits of equal shape and computes a loss per entry. `reduce_mean` chooses the example denominator. Compare `probability>=threshold` for a declared tie policy. Do not apply sigmoid twice or feed a probability to a function that expects a logit; both can produce finite but incorrectly interpreted losses.

## Exercise 1: Convert scores

The question is: Convert logits [-2, 0, 2] into probabilities and inspect the central value.

The sigmoid is monotonic, so ordering survives. A score of zero lies at the probability midpoint, which makes it a useful exact boundary fixture.

```python
z = tf.constant([-2.0, 0.0, 2.0])
p = tf.math.sigmoid(z).numpy()
assert p[1] == 0.5 and np.all(np.diff(p) > 0)
```

**Expected:** middle probability 0.5; probabilities increase.

**Verify:** In a fresh process, the exercise checks confirm `p[1] == 0.5` and `np.all(np.diff(p) > 0)`.

## Exercise 2: Check the midpoint loss

The question is: Calculate positive-label binary cross entropy at zero logit.

A fifty-fifty prediction assigns probability one half to either outcome. Its negative logarithm provides an independent reference that does not depend on a trained model.

```python
loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant([1.0]), logits=tf.constant([0.0]))
np.testing.assert_allclose(loss.numpy(), [np.log(2)], atol=1e-6, rtol=0)
```

**Expected:** loss \(\log(2)\) within 1e-6.

**Verify:** In a fresh process, the exercise checks confirm `loss.numpy()` matches `[np.log(2)]` within 1e-6.

## Exercise 3: Move the threshold

The question is: Compare decisions at thresholds 0.5 and 0.8, counting a probability equal to the threshold as positive.

Only the middle decision changes. Save scores independently from decisions so threshold exploration does not look like a second model fitting operation.

```python
assert (p >= 0.5).tolist() == [False, True, True]
assert (p >= 0.8).tolist() == [False, False, True]
```

**Expected:** decisions [False, True, True] versus [False, False, True].

**Verify:** In a fresh process, the exercise checks confirm `(p >= 0.5).tolist() == [False, True, True]` and `(p >= 0.8).tolist() == [False, False, True]`.

## Exercise 4: Expose a convention mismatch

The question is: Treat probability 0.5 as if it were a logit and compare the positive-label loss with log 2.

The mistaken argument is interpreted as a score favoring the positive class. The API cannot infer that the caller intended a probability; explicit naming and shape contracts are necessary.

```python
wrong = float(
    tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant(1.0), logits=tf.constant(0.5))
)
assert abs(wrong - np.log(2)) > 0.1
```

**Expected:** wrong loss differs from log 2 by more than 0.1.

**Verify:** In a fresh process, the exercise checks confirm `abs(wrong - np.log(2)) > 0.1`.

## Exercise 5: Stress large scores

The question is: Calculate losses for logits 1000, -1000 with labels 1, 0 using the logits-aware form.

A naive `log(sigmoid())` path can lose precision at extreme probabilities. The stable form handles the algebra before exponentiation creates overflow or logarithms receive rounded zero.

```python
stable = tf.nn.sigmoid_cross_entropy_with_logits(
    labels=tf.constant([1.0, 0.0]), logits=tf.constant([1000.0, -1000.0])
).numpy()
assert np.isfinite(stable).all()
np.testing.assert_allclose(stable, [0, 0], atol=1e-6, rtol=0)
```

**Expected:** both finite losses approximately 0.

**Verify:** In a fresh process, the exercise checks confirm `np.isfinite(stable).all()` and `stable` matches `[0, 0]` within 1e-6.

## Exercise 6: Count decisions separately

The question is: For labels [0, 1, 1], count errors under the two thresholds.

This count is a decision metric. It does not replace the probability loss and cannot show that threshold 0.5 is optimal for a different cost structure or population.

```python
labels = np.array([0, 1, 1])
assert np.count_nonzero((p >= 0.5) != labels) == 0
assert np.count_nonzero((p >= 0.8) != labels) == 1
```

**Expected:** 0 errors at 0.5 and 1 at 0.8 on this fixture.

**Verify:** In a fresh process, the exercise checks confirm `np.count_nonzero((p >= 0.5) != labels) == 0` and `np.count_nonzero((p >= 0.8) != labels) == 1`.

## Review after comparison

Change one fixture value in exercise 4, Expose a convention mismatch, and predict the new result before running it. Keep the failing version of exercise 5, Stress large scores, next to its repair. A missing framework is an environment record, not a failed assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
