# torch-017: Dropout, regularization, train and eval modes

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-016`.

## Learning objectives

Separate explicit regularization penalties from Dropout's train and eval behavior and check each with exact values.

Central investigation: Compute L1 and squared L2 penalties for weights [1, -2], run Dropout(0.5) in eval and train mode and differentiate the penalty.

Finish condition: L1 is 3 and squared L2 is 5, eval-mode Dropout returns its input exactly, train mode outputs only 0 or 2, a 0.1 coefficient adds a penalty of 0.5 for a total of 2.5, and the penalty gradient is [0.2, -0.4].

## Purpose and mental model

Regularization and training mode affect different parts of the experiment. An explicit L1orL2penalty adds a term to the objective. Dropout randomly zeroes activations during training and rescales retained values; in evaluation it returns the unmodified input. model.train and model.eval recursively set module behavior, but neither changes whether autograd records operations. Optimizer weight decay and an explicit penalty can have different semantics, especially for adaptive optimizers, so their names do not establish equivalence.

The fixture uses weights 1, -2 and unit activations. It separates data loss from penalty, checks stochastic outputs by allowed values rather than a fixed random mask, and confirms deterministic evaluation. None of these checks proves that regularization improves held-out quality; that requires a controlled validation comparison.

## Design decisions and when to use this method

Select a regularizer against a held-out criterion that reflects the intended task, and keep the data-loss term visible. A smaller parameter norm or a stochastic training curve is mechanism evidence, not evidence that prediction improved. Compare a declared baseline, coefficient, seed policy and stopping rule before attributing a change to regularization.

Use model mode to control stochastic modules and gradient mode to control differentiation. These controls serve different purposes. Evaluation with gradients is appropriate for sensitivity analysis, while no_grad on a model left in training mode can still sample Dropout and update BatchNorm buffers. When choosing optimizer weight decay, inspect the actual update rule and the parameter groups to which it applies.

## Paired TensorFlow comparison

Compare [tf-017](../../deep-learning-tensorflow/guides/tf-017.md) after deriving the shared numerical contract.

Keras commonly receives training=True/False per call; PyTorch modules store train/eval mode. Both need explicit stochastic-layer behavior. Keras regularizers and PyTorch optimizer weight_decay are not automatically identical; compare the actual objective or update rule.

## Vocabulary and concepts

**Regularization penalty:** A parameter-dependent term added to the training objective.

**Dropout mode:** Whether stochastic activation masking is applied.

**Weight decay:** An optimizer-specific parameter update policy requiring its own contract.

## How to run this lesson

Run `torch-017` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C reuse `drop` and `x` from earlier blocks; run all three in order.

## Syntax anatomy and reasoning sequence

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

## Worked example / walkthrough

### Example A: Calculate two penalties

The squared L2penalty is not the square root norm. Naming the convention avoids a factor or square-root mismatch when comparing implementations.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w = torch.tensor([1.0, -2.0])
assert w.abs().sum().item() == 3 and w.square().sum().item() == 5
```

**Expected:** \(L_{1}=3\); squared \(L_{2}=5\).

### Example B: Check evaluation dropout

The local inference behavior is deterministic. Other pipeline components can still be random, so a full model needs its own evaluation contract.

```python
drop = nn.Dropout(0.5)
drop.eval()
x = torch.ones((4, 8))
assert torch.equal(drop(x), x) and torch.equal(drop(x), x)
```

**Expected:** both outputs exactly ones.

### Example C: Check training invariants

The test does not require a particular mask or count of zeros. Such a pattern would overfit the random implementation rather than the Dropout contract.

```python
drop.train()
sampled = drop(x)
assert tuple(sampled.shape) == (4, 8) and set(sampled.unique().tolist()) <= {0.0, 2.0}
```

**Expected:** shape (4, 8); only 0 or 2.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Calculate two penalties. Predict exercise 6, Keep mode separate from gradients, from its prompt alone: Set Dropout to eval and pass a requires_grad input. Then explain why this finish condition holds: L1 is 3 and squared L2 is 5, eval-mode Dropout returns its input exactly, train mode outputs only 0 or 2, a 0.1 coefficient adds a penalty of 0.5 for a total of 2.5, and the penalty gradient is [0.2, -0.4]. Keep each prediction beside the observed value.

## Exercises

1. **Compute penalties for a new vector.** Use weights 3, -4, 0 and compute the L1 and squared L2 sums.
   **Expected:** L1 = 7; squared L2 = 25.
   **Verify:** In a fresh process, the exercise checks confirm `penalized.abs().sum().item() == 7` and `penalized.square().sum().item() == 25`.

2. **Predict train-mode values for p=0.25.** Apply Dropout(0.25) in train mode to a (3, 5) tensor of ones and inspect every value.
   **Expected:** shape (3, 5); each value is 0 or 4/3.
   **Verify:** In a fresh process, the exercise checks confirm `tuple(kept.shape) == (3, 5)` and `all((value == 0 or abs(value - 4 / 3) < 1e-06 for value in kept.flatten().tolist()))`.

3. **Confirm eval disables the new rate.** Switch the same Dropout(0.25) layer to eval mode and apply it to the ones tensor.
   **Expected:** output exactly equals the input.
   **Verify:** In a fresh process, the exercise checks confirm `torch.equal(quarter(torch.ones((3, 5))), torch.ones((3, 5)))`.

4. **Separate data and penalty terms.** Combine data loss 2 with coefficient 0.1 times squared L2.
   **Expected:** penalty 0.5; total 2.5.
   **Verify:** In a fresh process, the exercise checks confirm `penalty.item() == 0.5` and `(data_loss + penalty).item() == 2.5`.

5. **Differentiate the explicit penalty.** Differentiate 0 \(0.1\cdot \operatorname{sum}(v\cdot v)\) at v=[1, -2].
   **Expected:** gradient [0.2, -0.4].
   **Verify:** In a fresh process, the exercise checks confirm `v.grad` matches `torch.tensor([0.2, -0.4])` within 1e-06.

6. **Keep mode separate from gradients.** Set Dropout to eval and pass a requires_grad input.
   **Expected:** output still requires grad; backward gives ones.
   **Verify:** In a fresh process, the exercise checks confirm `observed.requires_grad` and `torch.equal(differentiable.grad, torch.ones(3))`.

## Common pitfalls and diagnosis

If evaluation predictions vary, inspect every stochastic input transformation and module's mode before blaming numerical precision. If no_grad did not stop the variation, remember that it does not switch Dropout into evaluation. If a frozen feature extractor changes behavior, inspect both its mode and its buffers rather than only requires_grad flags.

If a regularization coefficient behaves differently after changing batch size or accumulation steps, write the complete numerator, denominator and penalty frequency. If two optimizers disagree, compare their state updates and whether decay enters the moments. If Dropout tests fail only because a different mask appears, replace the random-pattern expectation with the declared shape/value invariants. If the objective improves but prediction quality does not, inspect the separately logged data loss and the independent validation population.

## Progressive hints

Hint 1: Example B (Check evaluation dropout) alters one assumption of Example A (Calculate two penalties). Hint 2: exercise 4, Separate data and penalty terms, should end at penalty 0.5; total 2.5. Work backward from it. Hint 3: exercise 5, Differentiate the explicit penalty, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Check training invariants, from its inputs alone. Predict whether exercise 3, Confirm eval disables the new rate, survives one changed input. Then explain Regularization penalty, Dropout mode, Weight decay in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Calculate two penalties) cannot be rebuilt without help, revisit `torch-016` first. `torch-018` (BatchNorm, LayerNorm and stateful normalization) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22 for the Regularization penalty, Dropout mode, Weight decay behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Does Dropout make each training batch mean exactly unchanged?**

No. It preserves an expectation under its random masking policy. A finite batch can have a different mean.

**Is weight decay always L2regularization?**

No. Equivalence depends on the optimizer and implementation. For adaptive optimizers, decoupled weight decay is not generally the same as adding a squared penalty to the gradient.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-017, Dropout, regularization, train and eval modes.
Read courses/deep-learning-pytorch/guides/torch-017.md and courses/deep-learning-pytorch/lessons/torch-017.py. Direct prerequisites: `torch-016`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
