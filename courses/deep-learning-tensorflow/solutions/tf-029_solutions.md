# tf-029: explanatory solutions

Open these answers for Precision, overflow and stable objectives after your own attempt at Example A, Expose naive overflow, or after an explicit reveal. Each answer reuses the guide's literal inputs, so a mismatch points to one step. The companion script runs the assertions; this page explains why they test Overflow, Log-sum-exp, Precision. After matching exercise 6, Validate input finiteness, invent a new input without looking here.

## Mechanism review

Floating-point arithmetic has a finite representable range. The probabilities implied by logits [1000,999] are well defined, but exponentiating those scores directly overflows ordinary floating-point types. Subtracting the maximum leaves the softmax unchanged because a common multiplicative factor cancels between numerator and denominator. A stable cross entropy works with shifted logits or a log-sum-exp expression, avoiding an unnecessary probability round trip. Numeric precision is a separate concern from objective correctness: a stable implementation can still optimize the wrong labels or denominator. Mixed precision may improve performance on some hardware, but this CPU fixture makes no speed claim.

**Overflow:** A finite mathematical result exceeds the numeric representation.

**Log-sum-exp:** A stable way to calculate the logarithm of a sum of exponentials.

**Precision:** The resolution of representable values, distinct from range.

## Reading the implementation

Use tf.nn.sparse_softmax_cross_entropy_with_logits for the combined stable calculation. In NumPy, logaddexp(0, -1) gives the positive-first-class loss. finite checks should include gradients as well as forward outputs. float16 overflows at much smaller exponent arguments than float64. Compare using absolute tolerances appropriate to the dtype instead of exact equality for transcendental functions.

## Exercise 1: Expose naive overflow

The question is: Exponentiate NumPy logits [1000,999] directly under an explicit error-state context.

The warning is intentionally scoped to a counterexample. Silencing all numerical warnings in a training program would hide unrelated failures.

```python
z = np.array([1000.0, 999.0])
with np.errstate(over="ignore"):
    naive = np.exp(z)
assert np.isinf(naive).all()
```

**Expected:** both exponentials are infinite.

**Verify:** In a fresh process, the exercise checks confirm `np.isinf(naive).all()`.

## Exercise 2: Calculate stable loss

The question is: Use a logits-aware TensorFlow loss for target 0.

The meaningful quantity is the difference between scores, not their shared offset. The stable form keeps that difference available without constructing enormous exponentials.

```python
loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
    labels=[0], logits=tf.constant([[1000.0, 999.0]])
)
np.testing.assert_allclose(loss.numpy(), [np.logaddexp(0, -1)], atol=1e-6, rtol=0)
```

**Expected:** loss \(\log(1+e^{-1})\) within 1e-6.

**Verify:** In a fresh process, the exercise checks confirm `loss.numpy()` matches `[np.logaddexp(0, -1)]` within 1e-6.

## Exercise 3: Check shift invariance

The question is: Compare `softmax([1000, 999])` with `softmax([0, -1])`.

A common score shift cancels from the normalized distribution. This metamorphic property can catch an implementation that normalizes the wrong axis or clips scores inconsistently.

```python
np.testing.assert_allclose(
    tf.nn.softmax(z).numpy(), tf.nn.softmax([0.0, -1.0]).numpy(), atol=1e-6, rtol=0
)
```

**Expected:** probabilities agree within 1e-6.

**Verify:** In a fresh process, the exercise checks confirm `tf.nn.softmax(z).numpy()` matches `tf.nn.softmax([0.0, -1.0]).numpy()` within 1e-6.

## Exercise 4: Inspect gradients

The question is: Differentiate the stable target 0 loss with respect to both logits.

The derivative of cross entropy is probability minus one-hot target. Its components sum to zero because the probabilities and target each sum to one.

```python
v = tf.Variable([[1000.0, 999.0]])
with tf.GradientTape() as tape:
    objective = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[0], logits=v))
g = tape.gradient(objective, v).numpy()
assert np.isfinite(g).all()
np.testing.assert_allclose(g.sum(), 0, atol=1e-6, rtol=0)
```

**Expected:** finite gradients summing approximately 0.

**Verify:** In a fresh process, the exercise checks confirm `np.isfinite(g).all()` and `g.sum()` matches `0` within 1e-6.

## Exercise 5: Separate precision policies

The question is: Compare float16 and float64 exponentiation of 20.

A lower-precision type changes range as well as resolution. Hardware support and loss scaling require separate experiments; a dtype cast alone is not evidence of safe mixed-precision training.

```python
with np.errstate(over="ignore"):
    low = np.exp(np.float16(20))
high = np.exp(np.float64(20))
assert np.isinf(low) and np.isfinite(high)
```

**Expected:** float16 overflows; float64 remains finite.

**Verify:** In a fresh process, the exercise checks confirm `np.isinf(low)` and `np.isfinite(high)`.

## Exercise 6: Validate input finiteness

The question is: Reject a NaN logit before using a maximum-subtracted softmax helper.

Maximum subtraction prevents a particular overflow mechanism. It does not turn NaN or infinity into a valid probability distribution, so validation remains necessary.

```python
def stable(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("finite vector")
    mass = np.exp(values - values.max())
    return mass / mass.sum()


try:
    stable([0, np.nan])
except ValueError:
    pass
else:
    raise AssertionError("NaN accepted")
np.testing.assert_allclose(stable(z).sum(), 1, atol=1e-12, rtol=0)
```

**Expected:** ValueError for NaN; finite input returns unit mass.

**Verify:** In a fresh process, the exercise checks confirm `stable([0, np.nan])` raises `ValueError` and `stable(z).sum()` matches `1` within 1e-12.

## Review after comparison

Change one fixture value in exercise 4, Inspect gradients, and predict the new result before running it. Keep the failing version of exercise 5, Separate precision policies, next to its repair. A missing framework is an environment record, not a failed assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
