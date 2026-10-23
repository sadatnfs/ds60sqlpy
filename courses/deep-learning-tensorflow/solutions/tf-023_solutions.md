# tf-023: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

An optimization loop can run without updating the intended parameter. A forward value calculated outside GradientTape may be disconnected even when its numeric value is correct. None means no recorded path, while a zero tensor means a recorded derivative evaluated to zero. Treating both as zero hides a model-construction failure. The loop must calculate loss inside the tape, request gradients for the intended variables, reject missing gradients, apply an update and recompute the post-update loss. A logged pre-update loss and post-update weight belong to different states. Tracing with tf.function changes how Python builds operations, so debug the eager state sequence first.

**Disconnected gradient:** No recorded differentiable path to the requested variable.

**Zero gradient:** A connected derivative whose current value is zero.

**State trace:** A record of values before and after each update.

## Reading the implementation

Use a new tape for every step. w.assign_sub(rate*gradient) mutates the tracked variable. Keep before/after weights as Python floats only for logging; converting the forward result to a NumPy value inside the loss would sever differentiation. Recompute yhat after assignment. The scalar pilot has a closed-form recurrence w_next=w-.1*(28/3)*(w-2).

## Exercise 1: Expose a missing path

The question is: Compute(w-2)² before opening a tape and ask that tape for its gradient.

The tape cannot reconstruct operations it never recorded. The numerical loss4 alone does not reveal this missing dependency.

```python
w=tf.Variable(0.,dtype=tf.float64); outside=(w-2)**2
with tf.GradientTape() as tape: loss=outside
assert tape.gradient(loss,w) is None
```

**Expected:** gradient is None.

**Verify:** Compare the computed values or written argument with gradient is None.

## Exercise 2: Distinguish an actual zero

The question is: Compute the same objective inside the tape atw2.

The path exists and its slope is zero at the optimum. Replacing every None with zero would make these semantically different observations indistinguishable.

```python
optimum=tf.Variable(2.,dtype=tf.float64)
with tf.GradientTape() as tape: loss=(optimum-2)**2
g=tape.gradient(loss,optimum); assert g is not None and float(g)==0
```

**Expected:** gradient is a tensor equal0.

**Verify:** Compare the computed values or written argument with gradient is a tensor equal0.

## Exercise 3: Repair two updates

The question is: Use x1,2,3,y2x,w0 and rate.1 for exactly2 steps.

The first update is28/15 and the second moves closer to2. This exact recurrence tests the loop order independently of framework metrics.

```python
x=tf.constant([1.,2.,3.],tf.float64); y=2*x; w=tf.Variable(0.,dtype=tf.float64); history=[]
for _ in range(2):
    with tf.GradientTape() as tape: loss=tf.reduce_mean((w*x-y)**2)
    g=tape.gradient(loss,w); assert g is not None
    w.assign_sub(.1*g); history.append(float(w))
np.testing.assert_allclose(float(w),448/225,atol=1e-12,rtol=0)
```

**Expected:** weight448/225 within1e-12.

**Verify:** Compare the computed values or written argument with weight448/225 within1e-12.

## Exercise 4: Recompute loss after assignment

The question is: Compare the two-step loss with the one-step loss56/675.

A loss tensor saved from before assignment does not retroactively change when the variable changes. The new loss requires a new forward calculation.

```python
after=float(tf.reduce_mean((w*x-y)**2))
assert 0<=after<56/675
```

**Expected:** two-step loss is smaller and nonnegative.

**Verify:** Compare the computed values or written argument with two-step loss is smaller and nonnegative.

## Exercise 5: Check gradient finiteness

The question is: Inject a nonfinite target and refuse to apply its gradient.

A bounded loop should check nonfinite state before contaminating weights. A skipped invalid update must be reported as a failure, not counted as a successful learning step.

```python
bad=tf.constant([2.,4.,np.inf],tf.float64); saved=float(w)
with tf.GradientTape() as tape: loss=tf.reduce_mean((w*x-bad)**2)
g=tape.gradient(loss,w)
assert not bool(tf.reduce_all(tf.math.is_finite(g))) and float(w)==saved
```

**Expected:** gradient is nonfinite and rejected before assignment.

**Verify:** Compare the computed values or written argument with gradient is nonfinite and rejected before assignment.

## Exercise 6: Compare an analytic recurrence

The question is: Calculate both updates with plain Python and compare each state with the tape trace.

Comparing every state identifies the first divergence. A final-value-only check can hide compensating errors or incorrect intermediate logging.

```python
oracle=0.; expected=[]
for _ in range(2): oracle-=.1*(28/3)*(oracle-2); expected.append(oracle)
np.testing.assert_allclose(history,expected,atol=1e-12,rtol=0)
```

**Expected:** both recorded states match within1e-12.

**Verify:** Compare the computed values or written argument with both recorded states match within1e-12.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
