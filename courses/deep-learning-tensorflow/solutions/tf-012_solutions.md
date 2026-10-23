# tf-012: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A regression investigation starts with a prediction unit and a split, not an optimizer. Here each row has three features and a deterministic target 2a-b+c. Four rows are reserved for fitting and two for assessment. A mean predictor is the baseline: it ignores features but provides a measured reference. A small linear model tests whether the features contain the intended relation. The split is fixed before any model decision. Training error shows fit to exposed records; holdout error measures only the two supplied unseen records, which is far too little for a broad reliability claim. Keep the arithmetic pilot alongside the final experiment because it tests an update independently of model quality.

**Baseline:** A simple prediction rule evaluated with the same split and metric.

**Holdout:** Records excluded from fitting and model selection.

**Evidence report:** Inputs, decisions, outputs and limits that make an experiment reviewable.

## Reading the implementation

The fixture is a float32 matrix with one row per observation. Slicing by saved IDs chooses rows in a known order. GradientTape differentiates mean squared residuals; SGD updates a three-by-one kernel. Compute the mean baseline from training targets only. A fixed loop limit makes runtime bounded and reports actual steps rather than treating a small loss as permission to continue indefinitely.

## Exercise 1: Freeze six records

The question is: Create the three-feature fixture below, assign IDs0..3 to train and4..5 to holdout, and calculate targets.

The target formula is specified before fitting. This makes the learning problem inspectable, while still requiring the optimizer to recover useful weights from only the training subset.

```python
x=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,1],[2,1,1]],dtype='float32'); y=x@np.array([[2.],[-1.],[1.]],dtype='float32')
train=[0,1,2,3]; test=[4,5]
assert not set(train)&set(test)
np.testing.assert_array_equal(y[:,0],[0,2,-1,1,2,4])
```

**Expected:** targets[0,2,-1,1,2,4], disjoint IDs.

**Verify:** Compare the computed values or written argument with targets[0,2,-1,1,2,4], disjoint IDs.

## Exercise 2: Measure the baseline

The question is: Use the training mean to predict both held-out targets and compute squared error.

Using the held-out mean would give the baseline access to assessment targets. Both the baseline and learned model must be evaluated on identical held-out IDs to support comparison.

```python
mean=float(y[train].mean()); baseline=float(np.mean((y[test]-mean)**2))
assert mean==.5 and baseline==7.25
```

**Expected:** training mean.5; holdout MSE7.25.

**Verify:** Compare the computed values or written argument with training mean.5; holdout MSE7.25.

## Exercise 3: Train a bounded model

The question is: Initialize a three-by-one kernel at zero and make exactly100 full-training SGD updates at rate.1.

The explicit step cap bounds the teaching run. Improvement is checked against the same initial training batch. It does not imply a universal learning-rate rule or a production acceptance threshold.

```python
w=tf.Variable(tf.zeros((3,1))); tx=tf.constant(x[train]); ty=tf.constant(y[train]); initial=float(tf.reduce_mean(ty**2))
for step in range(100):
    with tf.GradientTape() as tape: loss=tf.reduce_mean((tx@w-ty)**2)
    w.assign_sub(.1*tape.gradient(loss,w))
train_error=float(tf.reduce_mean((tx@w-ty)**2))
assert step+1==100 and train_error<initial and np.isfinite(w.numpy()).all()
```

**Expected:** 100 updates; finite weights; training error below its initial value.

**Verify:** Compare the computed values or written argument with 100 updates; finite weights; training error below its initial value.

## Exercise 4: Open the holdout once

The question is: Compute held-out MSE after the fixed100 updates and compare it with the frozen baseline.

Report training and held-out errors separately. The small test count is part of the result, not an inconvenient detail to suppress. Do not restart tuning after inspecting this value.

```python
test_error=float(np.mean((x[test]@w.numpy()-y[test])**2))
assert test_error<baseline
report={'train_mse':train_error,'test_mse':test_error,'test_count':2,'steps':100}
assert report['test_count']==2
```

**Expected:** holdout error below7.25 on the two supplied records.

**Verify:** Compare the computed values or written argument with holdout error below7.25 on the two supplied records.

## Exercise 5: Preserve arithmetic evidence

The question is: Derive a one-feature pilot update from x1,2,3 and target2x at w0,rate.1.

A scalar diagnostic is a separate implementation check, not an alternative score for the three-feature model. Keeping both prevents an impressive-looking fit from concealing a broken update.

```python
pilot=np.array([1.,2.,3.]); gradient=2*np.mean((-2*pilot)*pilot); updated=-.1*gradient
np.testing.assert_allclose([updated,np.mean((updated*pilot-2*pilot)**2)],[28/15,56/675],atol=1e-12,rtol=0)
```

**Expected:** weight28/15 and loss56/675.

**Verify:** Compare the computed values or written argument with weight28/15 and loss56/675.

## Exercise 6: Reject a false conclusion

The question is: Construct a report containing split IDs, errors, step count and limitations; refuse a production-quality claim from two holdout rows.

A reproducible experiment may still be too small for the intended decision. The correct result can be a limited demonstration with explicit next evidence, rather than an unsupported release recommendation.

```python
report.update(train_ids=train,test_ids=test,limitation='Two synthetic holdout rows do not establish population reliability.')
assert report['test_ids']==[4,5] and 'do not establish' in report['limitation']
```

**Expected:** report names2 holdout records and makes no population guarantee.

**Verify:** Compare the computed values or written argument with report names2 holdout records and makes no population guarantee.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
