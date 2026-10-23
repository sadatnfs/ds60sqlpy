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

UseX shaped(4, 1), floating binary targets and nn.Linear(1, 1, bias=False). Calculate x.std(dim=0, correction=0)to match the declared population normalization fixture. Train with BCEWithLogitsLoss for40fixed SGD updates. Evaluate with model.eval and no_grad, then classify logits>=0. Count TP, TN, FP, FN with boolean masks and verify their sum.

## Exercise 1: Freeze the geometric task

The question is: Use training x-2, -1, 1, 2 with labels0, 0, 1, 1 and test x-3, 3.

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

PyTorch's default sample correction would produce a different scale. Specifying correction0aligns this fixture with the paired TensorFlow/NumPy calculation.

```python
mean=x.mean(0); scale=x.std(0,correction=0); tx=(x-mean)/scale; vx=(test_x-mean)/scale
assert mean.item()==0; np.testing.assert_allclose(scale.item(),np.sqrt(2.5),atol=1e-6,rtol=0)
```

**Expected:** mean0; scale sqrt2.5.

**Verify:** Compare the computed values or written argument with mean0; scale sqrt2.5.

## Exercise 3: Train a fixed classifier

The question is: Zero-initialize the weight and run40SGD.1 steps with binary logits loss.

The fixed budget is part of the experiment. It is not repeated until the test happens to look favorable.

```python
model=nn.Linear(1,1,bias=False)
with torch.no_grad(): model.weight.zero_()
optimizer=torch.optim.SGD(model.parameters(),lr=.1)
for _ in range(40):
    optimizer.zero_grad(set_to_none=True); loss=F.binary_cross_entropy_with_logits(model(tx),y); loss.backward(); optimizer.step()
assert model.weight.item()>0 and torch.isfinite(model.weight).all()
```

**Expected:** positive finite weight after40 updates.

**Verify:** Compare the computed values or written argument with positive finite weight after40 updates.

## Exercise 4: Account for every test prediction

The question is: Threshold test logits at0 and calculate confusion counts.

The conservation check prevents dropped or duplicated test rows from silently changing the metric.

```python
model.eval()
with torch.no_grad(): prediction=model(vx).ravel()>=0
counts={'tp':int((prediction&truth).sum()),'tn':int((~prediction&~truth).sum()),'fp':int((prediction&~truth).sum()),'fn':int((~prediction&truth).sum())}
assert counts=={'tp':1,'tn':1,'fp':0,'fn':0} and sum(counts.values())==2
```

**Expected:** TP1, TN1, FP0, FN0, total2.

**Verify:** Compare the computed values or written argument with TP1, TN1, FP0, FN0, total2.

## Exercise 5: Compare a constant baseline

The question is: Predict class0for both test rows and count mistakes.

The comparison uses identical test units. It does not justify a population claim from two cases.

```python
baseline=torch.zeros(2,dtype=torch.bool)
assert int((baseline!=truth).sum())==1 and int((prediction!=truth).sum())==0
```

**Expected:** baseline1error; model0on this fixture.

**Verify:** Compare the computed values or written argument with baseline1error; model0on this fixture.

## Exercise 6: Reveal a group-specific failure

The question is: Flip only the positive group decision and report group counts.

A global error rate of one-half would hide the entire failure in the positive group. Counts and group meaning belong beside the aggregate.

```python
broken=prediction.clone(); broken[1]=False
report={group:(int(broken[i]!=truth[i]),1) for i,group in enumerate(['negative','positive'])}
assert report=={'negative':(0,1),'positive':(1,1)}
```

**Expected:** negative0/1errors; positive1/1.

**Verify:** Compare the computed values or written argument with negative0/1errors; positive1/1.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
