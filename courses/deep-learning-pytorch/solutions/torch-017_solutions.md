# torch-017: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Regularization and training mode affect different parts of the experiment. An explicit L1orL2penalty adds a term to the objective. Dropout randomly zeroes activations during training and rescales retained values; in evaluation it returns the unmodified input. model.train and model.eval recursively set module behavior, but neither changes whether autograd records operations. Optimizer weight decay and an explicit penalty can have different semantics, especially for adaptive optimizers, so their names do not establish equivalence.

The fixture uses weights 1, -2 and unit activations. It separates data loss from penalty, checks stochastic outputs by allowed values rather than a fixed random mask, and confirms deterministic evaluation. None of these checks proves that regularization improves held-out quality; that requires a controlled validation comparison.

**Regularization penalty:** A parameter-dependent term added to the training objective.

**Dropout mode:** Whether stochastic activation masking is applied.

**Weight decay:** An optimizer-specific parameter update policy requiring its own contract.

## Reading the implementation

nn.Dropout(p=.5) scales retained training activations by 1/(1-p). Call train or eval to select behavior. Compute sum(abs(w)) and sum(w²) for declared penalty conventions, then multiply by an explicit coefficient. A half-scaled squared penalty would have a different derivative. Keep metrics and penalty components separate in logs.

## Derive the objective, random transformation and gradient

The fixture has w=[1, -2]. The absolute-value sum is three, the squared-value sum is five, and the Euclidean norm is sqrt(5). These are different quantities. This chapter's squared L2 penalty is lambda times the sum of squared weights, without a one-half factor. At lambda=0.1 it contributes 0.5 to the objective and gradient[0.2, -0.4]. Doubling both weights doubles the L1 sum to six but quadruples the squared sum to twenty. That scale dependence matters when preprocessing changes the meaning of a unit weight.

Suppose one coordinate has data gradient g=0.3, parameter w=1 and learning rate eta=0.1. Ordinary SGD on data loss plus 0.1*w² uses total gradient 0.3+0.2=0.5 and gives w'=0.95. The update can also be written (1-2*eta*lambda)w-eta*g. An SGD weight-decay coefficient 0.2 corresponds to this particular explicit penalty convention. A coefficient 0.1 would correspond to a half-scaled objective and would instead give 0.96 for this example. A shared name or numeric coefficient does not fix the objective's convention.

For an adaptive optimizer, adding 2*lambda*w to g also changes the moment estimates and coordinatewise scaling. Decoupled AdamW applies its decay separately from those moment calculations. Consequently the SGD algebra above does not establish an Adam/AdamW equivalence. Compare the optimizer formula, update count, learning-rate schedule and decayed parameter groups. [PyTorch 2.9 AdamW](https://docs.pytorch.org/docs/2.9/generated/torch.optim.AdamW.html).

Loss reduction adds another scale choice. Replacing a mean over B observations with a sum multiplies the data gradient by B but leaves a separately added fixed penalty unchanged. That reduces the relative penalty strength unless its coefficient is adjusted. Repeating the full penalty at each microbatch also changes its total contribution if the intent was one large-batch objective. Specify whether the penalty is applied once per optimizer step and how accumulated data gradients are normalized.

For Dropout probability p<1, let m be a Bernoulli keep indicator with probability q=1-p. Inverted Dropout computes y=m*x/q during training. Thus E[y]=x and Var(y)=x²*p/q. This statement conditions on the input value; it does not assert that a finite collection of outputs has exactly the same mean. At p=0.5 and x=1, each output is zero or two, each with probability one-half. The derivative with respect to x is the same multiplier m/q, so the sampled backward path is either zero or two. During evaluation the transformation is identity. [PyTorch 2.9 Dropout](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Dropout.html).

The fixture contains 32 unit activations. Under independent elementwise masking, the count K of retained values has mean 16 and variance 8. The observed tensor mean is 2 K/32, so its expectation is one and its variance is 1/32. Its standard deviation is about 0.177. A particular call can retain 15 or 18 values without violating the contract. Even all-zero and all-two tensors are possible, though rare. That is why the executable assertion checks shape and allowed values rather than requiring exactly 16 survivors or a particular cross-platform random mask.

Expected activation preservation also does not imply preservation after nonlinear downstream operations. If a scalar activation is always one without Dropout, its square is one. With p=0.5, its squared dropped value is zero or four and has expectation two. Therefore a model's expected squared loss need not equal its loss at the expected activation. Dropout changes the stochastic training objective, not just the way an unchanged loss is sampled.

The state table helps prevent accidental coupling of unrelated controls:

| Configuration | Dropout mask | Autograd recording for eligible inputs |
| --- | --- | --- |
| train mode, ordinary grad mode | Sampled | Enabled |
| eval mode, ordinary grad mode | Identity | Enabled |
| train mode inside no_grad | Sampled | Disabled |
| eval mode inside no_grad | Identity | Disabled |

Exercise six deliberately uses the second row: an evaluation-mode Dropout still carries derivatives, and summing its identity output gives an all-ones input gradient. An inference service commonly uses the fourth row, but gradient-based explanation or adversarial sensitivity analysis may intentionally use the second. Monte Carlo Dropout requires its own deliberate mode policy; simply switching an entire model to train can also change unrelated BatchNorm state.

For an interview, explain why a training loss can rise after regularization while validation loss improves: the optimized objective includes a penalty or stochastic computation, so it is not the same measured quantity as deterministic predictive loss. Then ask whether the validation comparison was selected repeatedly and whether independent evidence remains. Conversely, lower weight norm by itself does not establish better calibrated probabilities, useful rankings or smaller out-of-population error.

## Exercise 1: Calculate two penalties

The question is: Use weights 1, -2 and compute L1and squared L2sums.

The squared L2penalty is not the square root norm. Naming the convention avoids a factor or square-root mismatch when comparing implementations.

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

**Expected:** shape(4, 8); only 0 or2.

**Verify:** Compare the computed values or written argument with shape(4, 8); only 0 or2.

## Exercise 4: Separate data and penalty terms

The question is: Combine data loss 2 with coefficient.1 times squared L2.

A total objective may change while the predictive error stays fixed. Logging components helps distinguish those mechanisms.

```python
data_loss=torch.tensor(2.); penalty=.1*w.square().sum()
assert penalty.item()==.5 and (data_loss+penalty).item()==2.5
```

**Expected:** penalty.5; total 2.5.

**Verify:** Compare the computed values or written argument with penalty.5; total 2.5.

## Exercise 5: Differentiate the explicit penalty

The question is: Differentiate .1*sum(v*v) at v=[1, -2].

The derivative contains 2*coefficient*v under this definition. Copying a coefficient from a half-scaled objective would change the update.

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
