# torch-024: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A classifier capstone must connect the task definition to training and evaluation evidence. The literal fixture classifies the sign of a scalar coordinate. Training and test IDs are fixed before fitting. Normalization statistics use only training rows, and the decision threshold is declared before test scoring. Aone-weight logistic model is sufficient for the fixture; unnecessary depth would obscure the experiment rather than improve its meaning.

Report confusion counts and their denominator, not only accuracy. A mean baseline or constant-class baseline provides a comparison under the same held-out units. Per-group failures can be hidden by an aggregate. The tiny test contains only two rows, so the capstone proves an inspectable local pipeline without establishing population reliability. PyTorch standard-deviation defaults differ from NumPy's population default, so the preprocessing comparison must set correction explicitly.

**Confusion matrix:** Counts of true/false positive and negative decisions.

**Frozen threshold:** A decision policy chosen before final assessment.

**Population standard deviation:** A variance calculation dividing by N rather than N-1.

**Subgroup evidence:** Errors and counts reported for a declared subset.

## Reading the implementation

Use X shaped (4, 1), floating binary targets and nn.Linear(1, 1, bias=False). Calculate `x.std(dim=0, correction=0)` to match the declared population normalization fixture. Train with BCEWithLogitsLoss for 40 fixed SGD updates. Evaluate with model.eval and no_grad, then classify \(\mathrm{logits}\ge 0\). Count TP, TN, FP, FN with boolean masks and verify their sum.

## Derive the classifier and audit every assessment row

The training values `[-2, -1, 1, 2]` have mean zero and squared deviations summing to ten. Population variance divides by four, giving 2.5 and scale \(\sqrt{2.5}\). PyTorch's `correction=0` matches NumPy's default used in the paired TensorFlow guide. Using the default sample correction would divide by three and produce \(\sqrt{\frac{10}{3}}\). Both scales are mathematically meaningful statistics, but they define different model inputs and update trajectories. Equal final class labels would not prove framework parity.

The stored model weight has shape(1, 1), inputs and targets have shape(4, 1), and logits have shape(4, 1). The bias is deliberately absent. Binary cross-entropy with logits is applied directly to those logits. Applying sigmoid first and then passing its output to the logits loss would change the objective. A target shaped(4, ) is also a different interface from(4, 1), even when it contains the same four numbers; preserve the declared axes rather than relying on broadcasting or reshaping after a failure.

For one normalized feature t and label y, the logit is \(z=\mathrm{wt}\) and the loss derivative with respect to w is \((\operatorname{sigmoid}(z)-y)t\). At \(w=0\), all probabilities are one-half. Writing \(s=\sqrt{2.5}\), the four derivative contributions are \(\frac{-1}{s}\), -1/(2s), -1/(2s), \(\frac{-1}{s}\). Their mean is -3/(4s), approximately-0.474342. The first SGD step at 0.1 therefore makes w approximately 0.0474342. This analytic sign and scale explain why the later fixed 40-step run should have a positive finite weight.

The data are separable under this one-feature rule. In an unregularized logistic model, continued loss reduction can push the weight larger without a finite optimum that must be reached. Forty steps are a declared computational budget, not evidence of convergence or a reason to repeat training until a preferred test score appears. If early stopping or hyperparameters are to be selected, they need a separate selection procedure and data boundary.

The decision rule is \(\mathrm{logit}\ge 0\), which corresponds to probability>=0.5. At the zero initial weight, both test logits are exactly zero and this tie convention predicts the positive class for both rows. After a positive weight, the transformed-3 point has a negative logit and the+3 point a positive one. The final confusion table is:

| Test input | Truth | Decision | Count category |
| --- | --- | --- | --- |
| -3 | negative | negative | \(\mathrm{TN}=1\) |
| +3 | positive | positive | \(\mathrm{TP}=1\) |

FP and FN are zero, and the four counts sum to two. The fixed class-zero baseline instead has \(\mathrm{TN}=1\), \(\mathrm{FN}=1\). Its one error and the model's zero errors are evaluated on the same two units. This is a useful paired comparison, but one changed decision would move accuracy by 50 percentage points, so the apparent difference is not a stable population estimate.

The subgroup counterexample changes only the positive row's decision. The negative group then has 0 errors out of 1 and the positive group 1 out of 1. Reporting only an aggregate error rate of \(\frac{1}{2}\) hides which group failed. At the same time, one observation per group is not sufficient for a reliable subgroup performance claim. These sign-based teaching groups are not a demonstrated fairness analysis of a real population.

Distinct train/test IDs are necessary but not sufficient for independence. Real data can contain copied examples, shared source families, temporal leakage or features only available after the decision. The literal fixture has none of those hidden sources by construction, but its rule is already visible to the learner. Preserve this difference between a procedure test and an undisclosed final assessment.

Finally, normalization parameters belong to the fitted artifact. The test coordinates must reuse the training mean and scale. Recomputing statistics on each inference batch changes predictions according to which other rows arrived together. A release should save feature order, units, mean, scale, dtype and threshold with the model state, and compare a known input through the complete preprocessing-and-model path. Model weights alone are not the whole predictor.

## Exercise 1: Freeze the geometric task

The question is: Use training x-2, -1, 1, 2 with labels 0, 0, 1, 1 and test x-3, 3.

The labels are defined from the fixture geometry before training. The holdout is not used to design a different target after seeing predictions.

```python
x=torch.tensor([[-2.],[-1.],[1.],[2.]]); y=torch.tensor([[0.],[0.],[1.],[1.]])
test_x=torch.tensor([[-3.],[3.]]); truth=torch.tensor([False,True]); train_ids={'a','b','c','d'}; test_ids={'e','f'}
assert not train_ids&test_ids and len(test_ids)==2
```

**Expected:** 4training records, 2test records.

**Verify:** Compare the computed values or written argument with 4training records, 2test records.

## Exercise 2: Fit explicit normalization

The question is: Calculate training mean and population standard deviation.

PyTorch's default sample correction would produce a different scale. Specifying correction 0 aligns this fixture with the paired TensorFlow/NumPy calculation.

```python
mean=x.mean(0); scale=x.std(0,correction=0); tx=(x-mean)/scale; vx=(test_x-mean)/scale
assert mean.item()==0; np.testing.assert_allclose(scale.item(),np.sqrt(2.5),atol=1e-6,rtol=0)
```

**Expected:** mean 0; scale sqrt 2.5.

**Verify:** Compare the computed values or written argument with mean 0; scale sqrt 2.5.

## Exercise 3: Train a fixed classifier

The question is: Zero-initialize the weight and run 40 SGD with rate 0.1 steps with binary logits loss.

The fixed budget is part of the experiment. It is not repeated until the test happens to look favorable.

```python
model=nn.Linear(1,1,bias=False)
with torch.no_grad(): model.weight.zero_()
optimizer=torch.optim.SGD(model.parameters(),lr=.1)
for _ in range(40):
    optimizer.zero_grad(set_to_none=True); loss=F.binary_cross_entropy_with_logits(model(tx),y); loss.backward(); optimizer.step()
assert model.weight.item()>0 and torch.isfinite(model.weight).all()
```

**Expected:** positive finite weight after 40 updates.

**Verify:** Compare the computed values or written argument with positive finite weight after 40 updates.

## Exercise 4: Account for every test prediction

The question is: Threshold test logits at 0 and calculate confusion counts.

The conservation check prevents dropped or duplicated test rows from silently changing the metric.

```python
model.eval()
with torch.no_grad(): prediction=model(vx).ravel()>=0
counts={'tp':int((prediction&truth).sum()),'tn':int((~prediction&~truth).sum()),'fp':int((prediction&~truth).sum()),'fn':int((~prediction&truth).sum())}
assert counts=={'tp':1,'tn':1,'fp':0,'fn':0} and sum(counts.values())==2
```

**Expected:** TP 1, TN 1, FP 0, FN 0, total 2.

**Verify:** Compare the computed values or written argument with TP 1, TN 1, FP 0, FN 0, total 2.

## Exercise 5: Compare a constant baseline

The question is: Predict class 0 for both test rows and count mistakes.

The comparison uses identical test units. It does not justify a population claim from two cases.

```python
baseline=torch.zeros(2,dtype=torch.bool)
assert int((baseline!=truth).sum())==1 and int((prediction!=truth).sum())==0
```

**Expected:** baseline 1 error; model 0 on this fixture.

**Verify:** Compare the computed values or written argument with baseline 1 error; model 0 on this fixture.

## Exercise 6: Reveal a group-specific failure

The question is: Flip only the positive group decision and report group counts.

A global error rate of one-half would hide the entire failure in the positive group. Counts and group meaning belong beside the aggregate.

```python
broken=prediction.clone(); broken[1]=False
report={group:(int(broken[i]!=truth[i]),1) for i,group in enumerate(['negative','positive'])}
assert report=={'negative':(0,1),'positive':(1,1)}
```

**Expected:** negative 0/1errors; positive \(\frac{1}{1}\).

**Verify:** Compare the computed values or written argument with negative 0/1errors; positive \(\frac{1}{1}\).

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
