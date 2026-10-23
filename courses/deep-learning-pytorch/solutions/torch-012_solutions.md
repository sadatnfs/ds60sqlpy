# torch-012: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

An auditable regressor combines data identity, a baseline, an explicit training loop and separate assessment. The three-feature fixture uses target2 a-b+c, so every row can be checked by hand. Four rows are used for fitting and two are reserved for assessment. A training-mean baseline provides a comparison that ignores features. The learned linear model updates under a fixed100-step budget without using the holdout to choose settings.

The capstone must report what it actually establishes. A small synthetic holdout can show that the implementation uses features in the intended way, but it cannot establish robustness or population accuracy. Keep the scalar arithmetic pilot from lesson008 as an independent mechanism check alongside the larger experiment. Hashing split IDs records identity; it does not prove the split design was appropriate.

**Experiment manifest:** The identities and settings needed to reconstruct a run.

**Training baseline:** A simple rule fitted only on training data.

**Frozen assessment:** Evaluation performed after model-selection choices are fixed.

## Reading the implementation

Create X shaped(6, 3), targets shaped(6, 1), and nn.Linear(3, 1, bias=False) with zero weights. Select rows by frozen index lists. Use MSELoss and SGD.1, zeroing gradients every step. Evaluate after the fixed budget under no_grad. Record train and holdout losses with their counts, plus model state and split identities. Do not overwrite the original split after seeing errors.

## Exercise 1: Create the three-feature fixture

The question is: Use rows zero, e1, e2, e3, [1, 1, 1], [2, 1, 1] and target2 a-b+c.

The target formula is part of the fixture definition. The learner can inspect it without relying on an opaque downloaded dataset.

```python
x=torch.tensor([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[1.,1.,1.],[2.,1.,1.]],dtype=torch.float64)
y=x@torch.tensor([[2.],[-1.],[1.]],dtype=torch.float64); train=[0,1,2,3]; test=[4,5]
torch.testing.assert_close(y[:,0],torch.tensor([0.,2.,-1.,1.,2.,4.],dtype=torch.float64),atol=0,rtol=0)
```

**Expected:** targets0, 2, -1, 1, 2, 4.

**Verify:** Compare the computed values or written argument with targets0, 2, -1, 1, 2, 4.

## Exercise 2: Measure the training-mean baseline

The question is: Fit the constant from training targets and score the two holdout rows.

The baseline receives the same assessment rows as the model, but its constant is fitted only on training targets.

```python
mean=y[train].mean(); baseline=((y[test]-mean)**2).mean()
assert mean.item()==.5 and baseline.item()==7.25
```

**Expected:** mean.5; holdout MSE7.25.

**Verify:** Compare the computed values or written argument with mean.5; holdout MSE7.25.

## Exercise 3: Train a bounded linear model

The question is: Initialize a bias-free3-to-1 Linear layer at zero and run100 SGD.1 updates.

The fixed budget is decided before assessment. A successful decrease demonstrates fitting on exposed data, not generalization by itself.

```python
model=nn.Linear(3,1,bias=False,dtype=torch.float64)
with torch.no_grad(): model.weight.zero_()
optimizer=torch.optim.SGD(model.parameters(),lr=.1); initial=((model(x[train])-y[train])**2).mean().item(); curve=[]
for _ in range(100):
    optimizer.zero_grad(set_to_none=True); loss=((model(x[train])-y[train])**2).mean(); curve.append(loss.item()); loss.backward(); optimizer.step()
assert len(curve)==100 and np.isfinite(curve).all() and curve[-1]<initial
```

**Expected:** 100 finite updates; training loss decreases.

**Verify:** Compare the computed values or written argument with 100 finite updates; training loss decreases.

## Exercise 4: Open the holdout after fitting

The question is: Calculate final training and holdout MSE without updates.

The score is specific to two authored holdout rows. Do not tune the learning rate after this observation and still call the same data untouched.

```python
model.eval()
with torch.no_grad(): train_error=((model(x[train])-y[train])**2).mean().item(); test_error=((model(x[test])-y[test])**2).mean().item()
assert np.isfinite([train_error,test_error]).all() and test_error<baseline.item()
```

**Expected:** finite errors; holdout error below7.25 on this fixture.

**Verify:** Compare the computed values or written argument with finite errors; holdout error below7.25 on this fixture.

## Exercise 5: Retain an independent pilot oracle

The question is: Calculate the scalar first update directly from NumPy without using the module.

The pilot protects the update mechanism independently of the feature model. A low final error could otherwise conceal a compensating implementation mistake.

```python
pilot=np.array([1.,2.,3.]); gradient=2*np.mean((-2*pilot)*pilot); updated=-.1*gradient
np.testing.assert_allclose([updated,np.mean((updated*pilot-2*pilot)**2)],[28/15,56/675],atol=1e-12,rtol=0)
```

**Expected:** w28/15 and loss56/675.

**Verify:** Compare the computed values or written argument with w28/15 and loss56/675.

## Exercise 6: Write the bounded evidence report

The question is: Record split IDs, 100 steps, errors and the two-row limitation.

The report should let a reviewer distinguish local software evidence from statistical reliability. A small successful fixture is a beginning, not a deployment certificate.

```python
report={'train_ids':train,'test_ids':test,'steps':100,'train_mse':train_error,'test_mse':test_error,'limit':'two synthetic holdout rows'}
assert not set(train)&set(test) and len(report['test_ids'])==2 and report['steps']==100
```

**Expected:** disjoint IDs; holdout count 2; explicit limited scope.

**Verify:** Compare the computed values or written argument with disjoint IDs; holdout count 2; explicit limited scope.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
