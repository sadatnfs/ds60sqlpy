# tf-024: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A classifier experiment needs more than an accuracy number. Define which rows are independent, freeze training/validation/test groups, fit preprocessing only on training data and choose decisions before opening the test partition. The fixture uses the sign of a geometric coordinate so its labels can be inspected directly. A tiny linear sigmoid classifier is sufficient; extra hidden layers are optional, not a requirement. Confusion counts retain the error types and must sum to the test cardinality. Per-group reporting reveals failures that an aggregate can hide. A capstone is complete when its data and evaluation contracts are defensible, even if its measured score is disappointing.

**Confusion counts:** Counts of correct and incorrect positive and negative decisions.

**Decision policy:** A frozen rule converting scores into predictions.

**Test unit:** The held-out entity counted once in final evaluation.

## Reading the implementation

Binary logits feed sigmoid cross entropy during training. After a fixed step budget, classify with \(\mathrm{logit}\ge 0\), equivalent to probability>=.5. Compute true-positive, false-positive, true-negative and false-negative counts with boolean masks. Keep counts as integers and divide only after establishing their denominators. Save the split IDs before any training operation.

## Exercise 1: Freeze geometry and groups

The question is: Use training points[-2,-1,1,2], labels[0,0,1,1]; hold out[-3,3].

The toy target is fully specified, so a learner can reason about errors without an opaque dataset. The holdout still has only two observations and cannot support broad conclusions.

```python
x=np.array([[-2.],[-1.],[1.],[2.]],dtype='float32'); y=np.array([[0.],[0.],[1.],[1.]],dtype='float32')
test_x=np.array([[-3.],[3.]],dtype='float32'); test_y=np.array([0,1]); train_ids={'a','b','c','d'}; test_ids={'e','f'}
assert not train_ids&test_ids and len(test_ids)==2
```

**Expected:** 4 train and2 test records with no shared IDs.

**Verify:** Compare the computed values or written argument with 4 train and2 test records with no shared IDs.

## Exercise 2: Fit training preprocessing

The question is: Calculate training mean and standard deviation, then apply them to both sets.

The test coordinates never enter the mean or scale calculation. A symmetric result is expected here because the training fixture itself is symmetric.

```python
mean=x.mean(0); scale=x.std(0); tx=(x-mean)/scale; vx=(test_x-mean)/scale
np.testing.assert_allclose(scale,[np.sqrt(2.5)],atol=1e-6,rtol=0)
assert mean[0]==0 and vx[0,0]==-vx[1,0]
```

**Expected:** mean0; scale sqrt2.5; test transformed symmetrically.

**Verify:** Compare the computed values or written argument with mean0; scale sqrt2.5; test transformed symmetrically.

## Exercise 3: Train within a fixed budget

The question is: Initialize one weight 0 and run40 full-batch SGD steps at rate 0.1 using binary logits loss.

The known sign relation creates a transparent diagnostic. The loop is intentionally bounded and does not tune its step count after viewing held-out predictions.

```python
w=tf.Variable([[0.]],dtype=tf.float32)
for step in range(40):
    with tf.GradientTape() as tape: loss=tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=y,logits=tf.constant(tx)@w))
    w.assign_sub(.1*tape.gradient(loss,w))
assert step+1==40 and float(w[0,0])>0 and np.isfinite(w.numpy()).all()
```

**Expected:** 40 finite updates and positive final weight.

**Verify:** Compare the computed values or written argument with 40 finite updates and positive final weight.

## Exercise 4: Account for every test row

The question is: Threshold final test logits at0 and compute all four confusion counts.

The sum is a conservation test. Dropping difficult rows or counting a repeated record twice would invalidate the reported metric even if the remaining predictions were correct.

```python
pred=(vx@w.numpy()).ravel()>=0; truth=test_y.astype(bool)
counts={'tp':int(np.sum(pred&truth)),'tn':int(np.sum(~pred&~truth)),'fp':int(np.sum(pred&~truth)),'fn':int(np.sum(~pred&truth))}
assert counts=={'tp':1,'tn':1,'fp':0,'fn':0} and sum(counts.values())==2
```

**Expected:** TP1,TN1,FP0,FN0; total2.

**Verify:** Compare the computed values or written argument with TP1,TN1,FP0,FN0; total2.

## Exercise 5: Compare a baseline

The question is: Predict class0 for every held-out row and report its error count beside the model.

The baseline uses the same held-out observations and decision unit. Its simplicity makes the gain interpretable, but the tiny count leaves substantial uncertainty.

```python
baseline=np.zeros(2,dtype=bool)
assert np.count_nonzero(baseline!=truth)==1 and np.count_nonzero(pred!=truth)==0
```

**Expected:** baseline1 error; model0 on2 records.

**Verify:** Compare the computed values or written argument with baseline1 error; model0 on2 records.

## Exercise 6: Expose a subgroup failure

The question is: Assign test groups negative and positive; flip only the positive prediction and report group errors.

The aggregate error rate would be one half. Naming the affected group and its denominator preserves the mechanism of the failure and avoids treating two groups as equally reliable.

```python
broken=pred.copy(); broken[1]=False
report={g:(int(broken[i]!=truth[i]),1) for i,g in enumerate(['negative','positive'])}
assert report=={'negative':(0,1),'positive':(1,1)}
```

**Expected:** negative0/1; positive1/1.

**Verify:** Compare the computed values or written argument with negative0/1; positive1/1.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
