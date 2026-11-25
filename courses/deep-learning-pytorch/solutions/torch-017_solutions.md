# torch-017: explanatory solutions

Open these answers only after attempting Dropout, regularization, train and eval modes yourself. They reuse the guide's literal inputs, starting from Example A, Calculate two penalties, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Regularization penalty, Dropout mode, Weight decay. After a pass, choose a new input for exercise 6, Keep mode separate from gradients, without looking.

After comparing, follow the [review steps](../STUDY-GUIDE.md#after-the-solutions).

## Mechanism review

Regularization and training mode affect different parts of the experiment. An explicit L1orL2penalty adds a term to the objective. Dropout randomly zeroes activations during training and rescales retained values; in evaluation it returns the unmodified input. model.train and model.eval recursively set module behavior, but neither changes whether autograd records operations. Optimizer weight decay and an explicit penalty can have different semantics, especially for adaptive optimizers, so their names do not establish equivalence.

The fixture uses weights 1, -2 and unit activations. It separates data loss from penalty, checks stochastic outputs by allowed values rather than a fixed random mask, and confirms deterministic evaluation. None of these checks proves that regularization improves held-out quality; that requires a controlled validation comparison.

**Regularization penalty:** A parameter-dependent term added to the training objective.

**Dropout mode:** Whether stochastic activation masking is applied.

**Weight decay:** An optimizer-specific parameter update policy requiring its own contract.

## Reading the implementation

nn.Dropout(\(p=0.5\)) scales retained training activations by \(\frac{1}{1-p}\). Call train or eval to select behavior. Compute sum(abs(w)) and \(\operatorname{sum}({w}^{2})\) for declared penalty conventions, then multiply by an explicit coefficient. A half-scaled squared penalty would have a different derivative. Keep metrics and penalty components separate in logs.

## Derive the objective, random transformation and gradient

The fixture has w=[1, -2]. The absolute-value sum is three, the squared-value sum is five, and the Euclidean norm is \(\sqrt{5}\). These are different quantities. This chapter's squared L2 penalty is lambda times the sum of squared weights, without a one-half factor. At \(\lambda=0.1\) it contributes 0.5 to the objective and gradient [0.2, -0.4]. Doubling both weights doubles the L1 sum to six but quadruples the squared sum to twenty. That scale dependence matters when preprocessing changes the meaning of a unit weight.

Suppose one coordinate has data gradient \(g=0.3\), parameter \(w=1\) and learning rate \(\eta=0.1\). Ordinary SGD on data loss plus \(0.1\cdot {w}^{2}\) uses total gradient \(0.3+0.2=0.5\) and gives w'=0.95. The update can also be written (1-2*eta*lambda)w-eta*g. An SGD weight-decay coefficient 0.2 corresponds to this particular explicit penalty convention. A coefficient 0.1 would correspond to a half-scaled objective and would instead give 0.96 for this example. A shared name or numeric coefficient does not fix the objective's convention.

For an adaptive optimizer, adding \(2\cdot \lambda\cdot w\) to g also changes the moment estimates and coordinatewise scaling. Decoupled AdamW applies its decay separately from those moment calculations. Consequently the SGD algebra above does not establish an Adam/AdamW equivalence. Compare the optimizer formula, update count, learning-rate schedule and decayed parameter groups. [PyTorch 2.9 AdamW](https://docs.pytorch.org/docs/2.9/generated/torch.optim.AdamW.html).

Loss reduction adds another scale choice. Replacing a mean over B observations with a sum multiplies the data gradient by B but leaves a separately added fixed penalty unchanged. That reduces the relative penalty strength unless its coefficient is adjusted. Repeating the full penalty at each microbatch also changes its total contribution if the intent was one large-batch objective. Specify whether the penalty is applied once per optimizer step and how accumulated data gradients are normalized.

For Dropout probability \(p<1\), let m be a Bernoulli keep indicator with probability \(q=1-p\). Inverted Dropout computes \(y=\frac{m\cdot x}{q}\) during training. Thus E[y]=x and \(\operatorname{Var}(y)=\frac{{x}^{2}\cdot p}{q}\). This statement conditions on the input value; it does not assert that a finite collection of outputs has exactly the same mean. At \(p=0.5\) and \(x=1\), each output is zero or two, each with probability one-half. The derivative with respect to x is the same multiplier m/q, so the sampled backward path is either zero or two. During evaluation the transformation is identity. [PyTorch 2.9 Dropout](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Dropout.html).

The fixture contains 32 unit activations. Under independent elementwise masking, the count K of retained values has mean 16 and variance 8. The observed tensor mean is 2 \(\frac{K}{32}\), so its expectation is one and its variance is \(\frac{1}{32}\). Its standard deviation is about 0.177. A particular call can retain 15 or 18 values without violating the contract. Even all-zero and all-two tensors are possible, though rare. That is why the executable assertion checks shape and allowed values rather than requiring exactly 16 survivors or a particular cross-platform random mask.

Expected activation preservation also does not imply preservation after nonlinear downstream operations. If a scalar activation is always one without Dropout, its square is one. With \(p=0.5\), its squared dropped value is zero or four and has expectation two. Therefore a model's expected squared loss need not equal its loss at the expected activation. Dropout changes the stochastic training objective, not just the way an unchanged loss is sampled.

The state table helps prevent accidental coupling of unrelated controls:

| Configuration | Dropout mask | Autograd recording for eligible inputs |
| --- | --- | --- |
| train mode, ordinary grad mode | Sampled | Enabled |
| eval mode, ordinary grad mode | Identity | Enabled |
| train mode inside no_grad | Sampled | Disabled |
| eval mode inside no_grad | Identity | Disabled |

Exercise six deliberately uses the second row: an evaluation-mode Dropout still carries derivatives, and summing its identity output gives an all-ones input gradient. An inference service commonly uses the fourth row, but gradient-based explanation or adversarial sensitivity analysis may intentionally use the second. Monte Carlo Dropout requires its own deliberate mode policy; simply switching an entire model to train can also change unrelated BatchNorm state.

For an interview, explain why a training loss can rise after regularization while validation loss improves: the optimized objective includes a penalty or stochastic computation, so it is not the same measured quantity as deterministic predictive loss. Then ask whether the validation comparison was selected repeatedly and whether independent evidence remains. Conversely, lower weight norm by itself does not establish better calibrated probabilities, useful rankings or smaller out-of-population error.

## Exercise 1: Compute penalties for a new vector

The question is: Use weights 3, -4, 0 and compute the L1 and squared L2 sums.

L1 adds absolute values; squared L2 adds squares, so the zero weight contributes to neither.

```python
penalized = torch.tensor([3.0, -4.0, 0.0])
assert penalized.abs().sum().item() == 7 and penalized.square().sum().item() == 25
```

**Expected:** L1 = 7; squared L2 = 25.

**Verify:** In a fresh process, the exercise checks confirm `penalized.abs().sum().item() == 7` and `penalized.square().sum().item() == 25`.

## Exercise 2: Predict train-mode values for p=0.25

The question is: Apply Dropout(0.25) in train mode to a (3, 5) tensor of ones and inspect every value.

Retained activations are scaled by \(\frac{1}{1-p}\) so the expected value stays 1; the exact retained pattern is random.

```python
quarter = nn.Dropout(0.25)
quarter.train()
kept = quarter(torch.ones((3, 5)))
assert tuple(kept.shape) == (3, 5) and all(
    value == 0 or abs(value - 4 / 3) < 1e-6 for value in kept.flatten().tolist()
)
```

**Expected:** shape (3, 5); each value is 0 or 4/3.

**Verify:** In a fresh process, the exercise checks confirm `tuple(kept.shape) == (3, 5)` and `all((value == 0 or abs(value - 4 / 3) < 1e-06 for value in kept.flatten().tolist()))`.

## Exercise 3: Confirm eval disables the new rate

The question is: Switch the same Dropout(0.25) layer to eval mode and apply it to the ones tensor.

Eval mode makes Dropout the identity regardless of p.

```python
quarter.eval()
assert torch.equal(quarter(torch.ones((3, 5))), torch.ones((3, 5)))
```

**Expected:** output exactly equals the input.

**Verify:** In a fresh process, the exercise checks confirm `torch.equal(quarter(torch.ones((3, 5))), torch.ones((3, 5)))`.

## Exercise 4: Separate data and penalty terms

The question is: Combine data loss 2 with coefficient 0.1 times squared L2.

A total objective may change while the predictive error stays fixed. Logging components helps distinguish those mechanisms.

```python
data_loss = torch.tensor(2.0)
penalty = 0.1 * w.square().sum()
assert penalty.item() == 0.5 and (data_loss + penalty).item() == 2.5
```

**Expected:** penalty 0.5; total 2.5.

**Verify:** In a fresh process, the exercise checks confirm `penalty.item() == 0.5` and `(data_loss + penalty).item() == 2.5`.

## Exercise 5: Differentiate the explicit penalty

The question is: Differentiate 0 \(0.1\cdot \operatorname{sum}(v\cdot v)\) at v=[1, -2].

The derivative contains 2*coefficient*v under this definition. Copying a coefficient from a half-scaled objective would change the update.

```python
v = torch.tensor([1.0, -2.0], requires_grad=True)
(0.1 * v.square().sum()).backward()
torch.testing.assert_close(v.grad, torch.tensor([0.2, -0.4]), atol=1e-6, rtol=0)
```

**Expected:** gradient [0.2, -0.4].

**Verify:** In a fresh process, the exercise checks confirm `v.grad` matches `torch.tensor([0.2, -0.4])` within 1e-06.

## Exercise 6: Keep mode separate from gradients

The question is: Set Dropout to eval and pass a requires_grad input.

Evaluation mode can be used with gradient-based analysis. Disable gradient recording separately when performing ordinary inference.

```python
drop.eval()
differentiable = torch.ones(3, requires_grad=True)
observed = drop(differentiable)
observed.sum().backward()
assert observed.requires_grad and torch.equal(differentiable.grad, torch.ones(3))
```

**Expected:** output still requires grad; backward gives ones.

**Verify:** In a fresh process, the exercise checks confirm `observed.requires_grad` and `torch.equal(differentiable.grad, torch.ones(3))`.

