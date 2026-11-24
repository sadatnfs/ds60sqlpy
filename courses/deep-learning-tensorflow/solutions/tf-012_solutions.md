# tf-012: explanatory solutions

Open these answers for Capstone: an auditable tiny regressor after your own attempt at Example A, Freeze six records, or after an explicit reveal. Each answer reuses the guide's literal inputs, so a mismatch points to one step. The companion script runs the assertions; this page explains why they test Baseline, Holdout, Evidence report. After matching exercise 6, Reject a false conclusion, invent a new input without looking here.

## Mechanism review

A regression investigation starts with a prediction unit and a split, not an optimizer. Here each row has three features and a deterministic target 2a-b+c. Four rows are reserved for fitting and two for assessment. A mean predictor is the baseline: it ignores features but provides a measured reference. A small linear model tests whether the features contain the intended relation. The split is fixed before any model decision. Training error shows fit to exposed records; holdout error measures only the two supplied unseen records, which is far too little for a broad reliability claim. Keep the arithmetic pilot alongside the final experiment because it tests an update independently of model quality.

**Baseline:** A simple prediction rule evaluated with the same split and metric.

**Holdout:** Records excluded from fitting and model selection.

**Evidence report:** Inputs, decisions, outputs and limits that make an experiment reviewable.

## Reading the implementation

The fixture is a float32 matrix with one row per observation. Slicing by saved IDs chooses rows in a known order. GradientTape differentiates mean squared residuals; SGD updates a three-by-one kernel. Compute the mean baseline from training targets only. A fixed loop limit makes runtime bounded and reports actual steps rather than treating a small loss as permission to continue indefinitely.

## Exercise 1: Freeze six records

The question is: Create the three-feature fixture below, assign IDs 0..3 to train and 4..5 to holdout, and calculate targets.

The target formula is specified before fitting. This makes the learning problem inspectable, while still requiring the optimizer to recover useful weights from only the training subset.

```python
x = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1], [2, 1, 1]], dtype="float32")
y = x @ np.array([[2.0], [-1.0], [1.0]], dtype="float32")
train = [0, 1, 2, 3]
test = [4, 5]
assert not set(train) & set(test)
np.testing.assert_array_equal(y[:, 0], [0, 2, -1, 1, 2, 4])
```

**Expected:** targets [0, 2, -1, 1, 2, 4], disjoint IDs.

**Verify:** In a fresh process, the exercise checks confirm `not set(train) & set(test)` and `y[:, 0]` equals `[0, 2, -1, 1, 2, 4]`.

## Exercise 2: Measure the baseline

The question is: Use the training mean to predict both held-out targets and compute squared error.

Using the held-out mean would give the baseline access to assessment targets. Both the baseline and learned model must be evaluated on identical held-out IDs to support comparison.

```python
mean = float(y[train].mean())
baseline = float(np.mean((y[test] - mean) ** 2))
assert mean == 0.5 and baseline == 7.25
```

**Expected:** training mean 0.5; holdout MSE 7.25.

**Verify:** In a fresh process, the exercise checks confirm `mean == 0.5` and `baseline == 7.25`.

## Exercise 3: Train a bounded model

The question is: Initialize a three-by-one kernel at zero and make exactly 100 full-training SGD updates at rate 0.1.

The explicit step cap bounds the teaching run. Improvement is checked against the same initial training batch. It does not imply a universal learning-rate rule or a production acceptance threshold.

```python
w = tf.Variable(tf.zeros((3, 1)))
tx = tf.constant(x[train])
ty = tf.constant(y[train])
initial = float(tf.reduce_mean(ty**2))
for step in range(100):
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean((tx @ w - ty) ** 2)
    w.assign_sub(0.1 * tape.gradient(loss, w))
train_error = float(tf.reduce_mean((tx @ w - ty) ** 2))
assert step + 1 == 100 and train_error < initial and np.isfinite(w.numpy()).all()
```

**Expected:** 100 updates; finite weights; training error below its initial value.

**Verify:** In a fresh process, the exercise checks confirm `step + 1 == 100`, `train_error < initial` and `np.isfinite(w.numpy()).all()`.

## Exercise 4: Open the holdout once

The question is: Compute held-out MSE after the fixed 100 updates and compare it with the frozen baseline.

Report training and held-out errors separately. The small test count is part of the result, not an inconvenient detail to suppress. Do not restart tuning after inspecting this value.

```python
test_error = float(np.mean((x[test] @ w.numpy() - y[test]) ** 2))
assert test_error < baseline
report = {"train_mse": train_error, "test_mse": test_error, "test_count": 2, "steps": 100}
assert report["test_count"] == 2
```

**Expected:** holdout error below 7.25 on the two supplied records.

**Verify:** In a fresh process, the exercise checks confirm `test_error < baseline` and `report['test_count'] == 2`.

## Exercise 5: Preserve arithmetic evidence

The question is: Derive a one-feature pilot update from x = [1, 2, 3] and target 2x at w = 0, rate 0.1.

A scalar diagnostic is a separate implementation check, not an alternative score for the three-feature model. Keeping both prevents an impressive-looking fit from concealing a broken update.

```python
pilot = np.array([1.0, 2.0, 3.0])
gradient = 2 * np.mean((-2 * pilot) * pilot)
updated = -0.1 * gradient
np.testing.assert_allclose(
    [updated, np.mean((updated * pilot - 2 * pilot) ** 2)], [28 / 15, 56 / 675], atol=1e-12, rtol=0
)
```

**Expected:** weight 28/15 and loss 56/675.

**Verify:** In a fresh process, the exercise checks confirm `[updated, np.mean((updated * pilot - 2 * pilot) ** 2)]` matches `[28 / 15, 56 / 675]` within 1e-12.

## Exercise 6: Reject a false conclusion

The question is: Construct a report containing split IDs, errors, step count and limitations; refuse a production-quality claim from two holdout rows.

A reproducible experiment may still be too small for the intended decision. The correct result can be a limited demonstration with explicit next evidence, rather than an unsupported release recommendation.

```python
report.update(
    train_ids=train,
    test_ids=test,
    limitation="Two synthetic holdout rows do not establish population reliability.",
)
assert report["test_ids"] == [4, 5] and "do not establish" in report["limitation"]
```

**Expected:** report names 2 holdout records and makes no population guarantee.

**Verify:** In a fresh process, the exercise checks confirm `report['test_ids'] == [4, 5]` and `'do not establish' in report['limitation']`.

## Review after comparison

Change one fixture value in exercise 4, Open the holdout once, and predict the new result before running it. Keep the failing version of exercise 5, Preserve arithmetic evidence, next to its repair. A missing framework is an environment record, not a failed assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
