# torch-017: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Regularization and training mode affect different parts of the experiment. An explicit L1 orL2 penalty adds a term to the objective. Dropout randomly zeroes activations during training and rescales retained values; in evaluation it returns the unmodified input. model.train and model.eval recursively set module behavior, but neither changes whether autograd records operations. Optimizer weight decay and an explicit penalty can have different semantics, especially for adaptive optimizers, so their names do not establish equivalence.

The fixture uses weights1, -2 and unit activations. It separates data loss from penalty, checks stochastic outputs by allowed values rather than a fixed random mask, and confirms deterministic evaluation. None of these checks proves that regularization improves held-out quality; that requires a controlled validation comparison.

**Regularization penalty:** A parameter-dependent term added to the training objective.

**Dropout mode:** Whether stochastic activation masking is applied.

**Weight decay:** An optimizer-specific parameter update policy requiring its own contract.

## Reading the implementation

nn.Dropout(p=.5) scales retained training activations by 1/(1-p). Call train or eval to select behavior. Compute sum(abs(w)) and sum(w²) for declared penalty conventions, then multiply by an explicit coefficient. A half-scaled squared penalty would have a different derivative. Keep metrics and penalty components separate in logs.

## Exercise 1: Calculate two penalties

The question is: Use weights1, -2 and compute L1 and squared L2 sums.

The squared L2 penalty is not the square root norm. Naming the convention avoids a factor or square-root mismatch when comparing implementations.

```python
w=torch.tensor([1.,-2.]); assert w.abs().sum().item()==3 and w.square().sum().item()==5
```

**Expected:** L1=3; squared L2=5.

**Verify:** Compare the computed values or written argument with L1=3; squared L2=5.

## Exercise 2: Check evaluation dropout

The question is: Apply Dropout.5 in eval mode to ones twice.

The local inference behavior is deterministic. Other pipeline components can still be random, so a full model needs its own evaluation contract.

```python
drop=nn.Dropout(.5); drop.eval(); x=torch.ones((4,8))
assert torch.equal(drop(x),x) and torch.equal(drop(x),x)
```

**Expected:** both outputs exactly ones.

**Verify:** Compare the computed values or written argument with both outputs exactly ones.

## Exercise 3: Check training invariants

The question is: Switch the same layer to train mode and inspect output values.

The test does not require a particular mask or count of zeros. Such a pattern would overfit the random implementation rather than the Dropout contract.

```python
drop.train(); sampled=drop(x)
assert tuple(sampled.shape)==(4,8) and set(sampled.unique().tolist())<={0.,2.}
```

**Expected:** shape(4, 8); only0 or2.

**Verify:** Compare the computed values or written argument with shape(4, 8); only0 or2.

## Exercise 4: Separate data and penalty terms

The question is: Combine data loss2 with coefficient.1 times squared L2.

A total objective may change while the predictive error stays fixed. Logging components helps distinguish those mechanisms.

```python
data_loss=torch.tensor(2.); penalty=.1*w.square().sum()
assert penalty.item()==.5 and (data_loss+penalty).item()==2.5
```

**Expected:** penalty.5; total2.5.

**Verify:** Compare the computed values or written argument with penalty.5; total2.5.

## Exercise 5: Differentiate the explicit penalty

The question is: Differentiate .1*sum(v*v) at v=[1, -2].

The derivative contains2*coefficient*v under this definition. Copying a coefficient from a half-scaled objective would change the update.

```python
v=torch.tensor([1.,-2.],requires_grad=True); (.1*v.square().sum()).backward()
torch.testing.assert_close(v.grad,torch.tensor([.2,-.4]),atol=1e-6,rtol=0)
```

**Expected:** gradient [.2, -.4].

**Verify:** Compare the computed values or written argument with gradient [.2, -.4].

## Exercise 6: Keep mode separate from gradients

The question is: Set Dropout to eval and pass a requires_grad input.

Evaluation mode can be used with gradient-based analysis. Disable gradient recording separately when performing ordinary inference.

```python
drop.eval(); differentiable=torch.ones(3,requires_grad=True); observed=drop(differentiable); observed.sum().backward()
assert observed.requires_grad and torch.equal(differentiable.grad,torch.ones(3))
```

**Expected:** output still requires grad; backward gives ones.

**Verify:** Compare the computed values or written argument with output still requires grad; backward gives ones.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
