# torch-017: Dropout, regularization, train and eval modes

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-016`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Regularization and training mode affect different parts of the experiment. The central investigation is concrete: Use weights 1, -2 and compute L1 and squared L2 sums. The finish condition is \(L_{1}=3\); squared \(L_{2}=5\). output still requires grad; backward gives ones. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

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

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-017`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-017.py` under `.learning/expansion/torch-017/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

nn.Dropout(p=.5) scales retained training activations by \(\frac{1}{1-p}\). Call train or eval to select behavior. Compute sum(abs(w)) and \(\operatorname{sum}({w}^{2})\) for declared penalty conventions, then multiply by an explicit coefficient. A half-scaled squared penalty would have a different derivative. Keep metrics and penalty components separate in logs.

## Derive the objective, random transformation and gradient

The fixture has w=[1, -2]. The absolute-value sum is three, the squared-value sum is five, and the Euclidean norm is \(\sqrt{5}\). These are different quantities. This chapter's squared L2 penalty is lambda times the sum of squared weights, without a one-half factor. At \(\lambda=0.1\) it contributes 0.5 to the objective and gradient[0.2, -0.4]. Doubling both weights doubles the L1 sum to six but quadruples the squared sum to twenty. That scale dependence matters when preprocessing changes the meaning of a unit weight.

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

w=torch.tensor([1.,-2.]); assert w.abs().sum().item()==3 and w.square().sum().item()==5
```

**Expected:** \(L_{1}=3\); squared \(L_{2}=5\).

### Example B: Check evaluation dropout

The local inference behavior is deterministic. Other pipeline components can still be random, so a full model needs its own evaluation contract.

```python
drop=nn.Dropout(.5); drop.eval(); x=torch.ones((4,8))
assert torch.equal(drop(x),x) and torch.equal(drop(x),x)
```

**Expected:** both outputs exactly ones.

### Example C: Check training invariants

The test does not require a particular mask or count of zeros. Such a pattern would overfit the random implementation rather than the Dropout contract.

```python
drop.train(); sampled=drop(x)
assert tuple(sampled.shape)==(4,8) and set(sampled.unique().tolist())<={0.,2.}
```

**Expected:** shape(4, 8); only 0 or2.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: \(L_{1}=3\); squared \(L_{2}=5\). output still requires grad; backward gives ones. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate two penalties.** Use weights 1, -2 and compute L1 and squared L2 sums.
   **Expected:** \(L_{1}=3\); squared \(L_{2}=5\).
   **Verify:** Save the assertion results for exercise 1, including \(L_{1}=3\); squared \(L_{2}=5\).

2. **Check evaluation dropout.** Apply Dropout.5 in eval mode to ones twice.
   **Expected:** both outputs exactly ones.
   **Verify:** Save the assertion results for exercise 2, including both outputs exactly ones.

3. **Check training invariants.** Switch the same layer to train mode and inspect output values.
   **Expected:** shape(4, 8); only 0 or2.
   **Verify:** Save the assertion results for exercise 3, including shape(4, 8); only 0 or2.

4. **Separate data and penalty terms.** Combine data loss 2 with coefficient.1 times squared L2.
   **Expected:** penalty.5; total 2.5.
   **Verify:** Save the assertion results for exercise 4, including penalty.5; total 2.5.

5. **Differentiate the explicit penalty.** Differentiate \(0.1\cdot \operatorname{sum}(v\cdot v)\) at v=[1, -2].
   **Expected:** gradient [.2, -.4].
   **Verify:** Save the assertion results for exercise 5, including gradient [.2, -.4].

6. **Keep mode separate from gradients.** Set Dropout to eval and pass a requires_grad input.
   **Expected:** output still requires grad; backward gives ones.
   **Verify:** Save the assertion results for exercise 6, including output still requires grad; backward gives ones.

## Common pitfalls and diagnosis

If evaluation predictions vary, inspect every stochastic input transformation and module's mode before blaming numerical precision. If no_grad did not stop the variation, remember that it does not switch Dropout into evaluation. If a frozen feature extractor changes behavior, inspect both its mode and its buffers rather than only requires_grad flags.

If a regularization coefficient behaves differently after changing batch size or accumulation steps, write the complete numerator, denominator and penalty frequency. If two optimizers disagree, compare their state updates and whether decay enters the moments. If Dropout tests fail only because a different mask appears, replace the random-pattern expectation with the declared shape/value invariants. If the objective improves but prediction quality does not, inspect the separately logged data loss and the independent validation population.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Regularization penalty, Dropout mode, Weight decay using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-016` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

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
