# torch-018: BatchNorm, LayerNorm and stateful normalization

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-017`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Normalization can introduce both state and cross-observation dependencies. The central investigation is concrete: Apply BatchNorm momentum.5 to rows 1, 3 and 3, 5. The finish condition is running mean 1, 2; batch counter 1. finite zeros with default affine initialization. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Normalization can introduce both state and cross-observation dependencies. BatchNorm uses batch statistics during training and updates running statistics for later inference. LayerNorm normalizes feature values within each record and does not mix unrelated batch rows. PyTorch BatchNorm momentum specifies the weight of the new batch statistic, whereas Keras momentum specifies the retention weight of the old statistic. Equal numeric momentum arguments therefore usually mean different updates.

PyTorch BatchNorm also distinguishes the variance estimate used for training normalization from the unbiased estimate used in the running-variance update. A comparison must name both. The fixture uses a batch with mean 2, 4 and momentum.5 to check running mean 1, 2 from zero. Evaluation must leave running state unchanged. Tokenwise LayerNorm is checked with a future-row perturbation to expose wrong-axis leakage.

## Design decisions and when to use this method

Choose normalization by the intended dependency structure. BatchNorm couples the values sharing a channel statistic during training, which can be appropriate for a batch-based feature model but requires representative batches and a deliberate inference-state policy. Tokenwise LayerNorm is useful when each token's features should be normalized without using other token positions. It does not by itself prevent information leakage elsewhere in a sequence model.

When transferring a model or comparing frameworks, specify layout, reduced axes, epsilon, affine parameters, training mode, variance estimators and stored state. Match a forward output and a state transition separately. A matching running mean or equal momentum argument is insufficient. Decide explicitly whether a frozen backbone should keep adapting its normalization buffers.

## Paired TensorFlow comparison

Compare [tf-018](../../deep-learning-tensorflow/guides/tf-018.md) after deriving the shared numerical contract.

The paired TensorFlow lesson includes momentum 0.5 and 0.8 probes, explicit population-variance moving state and Keras BatchNorm trainable=False behavior. PyTorch momentum weights the new batch statistic; Keras momentum retains the old statistic. Translate the coefficient, then separately compare reduction axes, variance estimators, epsilon, affine parameters and mode behavior. Matching the running mean does not establish output or full-state parity.

## Vocabulary and concepts

**Running statistic:** Persistent state updated from training batches.

**Momentum convention:** Which coefficient weights the old versus new statistic.

**Batch coupling:** One observation influencing another through shared statistics.

**LayerNorm axis:** The feature dimensions normalized within one observation.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-018`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-018.py` under `.learning/expansion/torch-018/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

nn.BatchNorm1d(2, momentum=.5) treats columns as features for an(N, C)input. train mode updates running_mean and running_var; eval mode uses stored state. nn.LayerNorm(2) reduces the last two-feature dimension independently for each row. Its default epsilon and affine parameters are part of the comparison. Track num_batches_tracked as a buffer, separate from trainable weight and bias.

## Trace normalization axes, state and derivatives

For each normalization group, define mean mu, population variance v and centered values \(c=x-\mu\). The internal normalized values are \(z=\frac{c}{\sqrt{v+\epsilon}}\); a learned scale gamma and offset beta then give \(y=\gamma\cdot z+\beta\). The grouping determines which other values can affect an output. The final tensor shape alone does not reveal that dependency.

| Layer and input | Statistics reduce over | Retained group identity | Affine parameter shape |
| --- | --- | --- | --- |
| BatchNorm1d on [N, C] | N | Channel C | [C] |
| BatchNorm1d on [N, C, L] | N and L | Channel C | [C] |
| BatchNorm2d on [N, C, H, W] | N, H, W | Channel C | [C] |
| LayerNorm(D) on [N, T, D] | D | Each [N, T] token | [D] |
| LayerNorm((T, D)) on [N, T, D] | T, D | Each N record | [T, D] |

The last two rows are different models. The first LayerNorm preserves token independence in its normalization statistics; the second lets future tokens affect earlier ones. On a channels-first image, LayerNorm(C) would act on the final axis only if that axis happens to have size C; it does not automatically interpret the second axis as channels. Reorder axes or choose the intended normalized_shape explicitly.

In the supplied BatchNorm fixture, columns[1, 3] and[3, 5] have means[2, 4]. Each centered column is[-1, 1]. Dividing the squared-deviation sum two by sample count two gives population variance one. Dividing by count minus one gives the unbiased estimate two. PyTorch uses the first estimate for training normalization and the second for updating running variance. Its momentum weights the new statistic. With default tracked statistics, eval uses stored state; setting track_running_stats=False changes that contract. [PyTorch 2.9 BatchNorm1d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BatchNorm1d.html).

With momentum 0.5, initial running mean zero and initial running variance one, the first update gives mean[1, 2] and variance[1.5, 1.5]. During that training call, however, the outputs use the current batch mean[2, 4] and population variance[1, 1], not those newly stored values. With initial \(\gamma=1\), \(\beta=0\), they are[[-1, -1], [1, 1]] divided by \(\sqrt{1+\epsilon}\). Calling eval afterward on the original batch instead gives[[0, 1], [2, 3]] divided by \(\sqrt{1.5+\epsilon}\). A changed output therefore does not require a changed trainable weight.

For a scalar fixed batch mean b, PyTorch momentum a gives r_t=(1-a)r_(t-1)+a*b. Starting from zero, the solution is \(r_{t}=(1-{\left(1-a\right)}^{t})\cdot b\). With \(a=0.2\) and b=[2, 4], the first two means are[0.4, 0.8] and[0.72, 1.44]. Keras expresses the same mean recurrence using retention momentum \(m=0.8\). If both APIs instead receive 0.2, their first means differ: PyTorch gives[0.4, 0.8] while Keras gives[1.6, 3.2]. The original 0.5 fixture hides this difference because a and 1-a coincide.

Mean-recursion matching still leaves variance state unmatched. The paired TensorFlow chapter's explicit two-row probe[0, 4] has population variance four and checks Keras moving variance \(0.5\cdot 1+0.5\cdot 4=2.5\). Its unbiased sample variance is eight, so the corresponding PyTorch running update would be \(0.5\cdot 1+0.5\cdot 8=4.5\). These are predictions from the named rules, not evidence that one should transplant a variance buffer between frameworks. The paired chapter contains the Keras execution contract, and this chapter's executable checks independently establish PyTorch's1.5 update on its own fixture. Epsilon and affine defaults must also be aligned before comparing outputs.

A useful geometric view is that centering removes the constant direction inside each group. For one LayerNorm group with d features, write \(g_{i}=\frac{\partial L}{\partial z_{i}}\) after incorporating any affine scale into the upstream gradient. Let \(s=\sqrt{v+\epsilon}\). Differentiating both the mean and variance gives

`dL/dx_i = (g_i - mean(g) - z_i*mean(g*z)) / s`.

This expression explains the dependency: an upstream derivative at one feature contributes to the means that influence other features in the same group. Summing the input derivatives gives zero, up to arithmetic error, because shifting all features by a common constant leaves the normalized values unchanged. The familiar exact removal of the radial direction is softened when epsilon is nonzero. Do not drop epsilon from a derivative calculation while retaining it in the forward pass.

For row[1, 3], \(\mu=2\), \(v=1\) and \(z=\frac{[-1,1]}{\sqrt{1+\epsilon}}\). Appending a separate row[100, 200] does not change this row under LayerNorm(2), since it belongs to a different group. Changing one of the first row's own features does affect both normalized outputs. LayerNorm computes its current input statistics in both train and eval modes and uses a biased variance estimate; its learned affine values can change the final output mean and variance. [PyTorch 2.9 LayerNorm](https://docs.pytorch.org/docs/2.9/generated/torch.nn.LayerNorm.html).

State freezing requires three independent questions. Are affine parameters receiving gradients? Can an optimizer update them? Can the layer mutate running buffers? Setting PyTorch BatchNorm weight and bias requires_grad=False addresses the first question, not the third. A train-mode call can still change running_mean, running_var and num_batches_tracked. Conversely eval can use fixed buffers while gradients still flow through affine parameters or inputs. These controls matter during transfer learning and sensitivity analysis.

Keras BatchNorm has a specific documented behavior: trainable=False selects inference behavior even for a direct call with training=True. The paired TensorFlow guide tests that rule. It is not a general equivalence between Keras trainable and PyTorch requires_grad, and it is not a claim about every Keras layer. Compiled Keras workflows also have their own recompilation rule after trainability changes. [Keras BatchNormalization](https://keras.io/api/layers/normalization_layers/batch_normalization/).

Small-batch and sequential applications need an additional assumption check. A single [1, C] training batch has no second observation per channel for the ordinary BatchNorm training contract; the lesson's singleton call deliberately occurs in eval after state exists. For [N, C, L], statistics include L, so using a whole sequence can couple future and past positions. A causal attention mask cannot undo that normalization dependency. State initialization, batch composition, last-batch policy and sequence layout therefore belong in the model contract, not only in a loader implementation detail.

## Worked example / walkthrough

### Example A: Update a running mean

The batch mean is 2, 4 and the new-statistic weight is.5. The result is not yet the full batch mean.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

bn=nn.BatchNorm1d(2,momentum=.5); x=torch.tensor([[1.,3.],[3.,5.]])
bn.train(); bn(x)
torch.testing.assert_close(bn.running_mean,torch.tensor([1.,2.]),atol=1e-6,rtol=0); assert bn.num_batches_tracked.item()==1
```

**Expected:** running mean 1, 2; batch counter 1.

### Example B: Freeze state during evaluation

Evaluation must not adapt to assessment batch composition. A forgotten eval call can mutate state and change predictions based on neighboring records.

```python
before=bn.running_mean.clone(); count=bn.num_batches_tracked.clone(); bn.eval(); bn(torch.tensor([[100.,200.]]))
assert torch.equal(before,bn.running_mean) and torch.equal(count,bn.num_batches_tracked)
```

**Expected:** running mean and batch counter unchanged.

### Example C: Check LayerNorm row independence

LayerNorm uses only the current row's features in this configuration. A sequence-wide or batch-wide reduction would fail the perturbation test.

```python
ln=nn.LayerNorm(2); alone=ln(torch.tensor([[1.,3.]])); together=ln(torch.tensor([[1.,3.],[100.,200.]]))
torch.testing.assert_close(alone[0],together[0],atol=1e-6,rtol=0)
```

**Expected:** first row matches within 1e-6.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: running mean 1, 2; batch counter 1. finite zeros with default affine initialization. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Update a running mean.** Apply BatchNorm momentum.5 to rows 1, 3 and 3, 5.
   **Expected:** running mean 1, 2; batch counter 1.
   **Verify:** Save the assertion results for exercise 1, including running mean 1, 2; batch counter 1.

2. **Freeze state during evaluation.** Call the trained layer in eval mode on 100, 200.
   **Expected:** running mean and batch counter unchanged.
   **Verify:** Save the assertion results for exercise 2, including running mean and batch counter unchanged.

3. **Check LayerNorm row independence.** Normalize 1, 3alone and beside 100, 200.
   **Expected:** first row matches within 1e-6.
   **Verify:** Save the assertion results for exercise 3, including first row matches within 1e-6.

4. **Inspect running variance convention.** From initial running variance 1, use batch values 1, 3whose unbiased variance is 2 and momentum.5.
   **Expected:** running variance 1.5 for each feature.
   **Verify:** Save the assertion results for exercise 4, including running variance 1.5 for each feature.

5. **Translate momentum explicitly.** Compute updates with old mean 0, batch mean 10 and PyTorch momentum.1versus Keras momentum.1.
   **Expected:** PyTorch 1; Keras 9 under their respective conventions.
   **Verify:** Save the assertion results for exercise 5, including PyTorch 1; Keras 9 under their respective conventions.

6. **Handle a constant feature row.** Apply LayerNorm to 5, 5 and inspect finiteness.
   **Expected:** finite zeros with default affine initialization.
   **Verify:** Save the assertion results for exercise 6, including finite zeros with default affine initialization.

## Common pitfalls and diagnosis

If normalization outputs disagree, first calculate one group's members and axes. Check whether the API's axis names a retained channel or a reduced feature dimension. Then compare current-batch statistics, stored statistics, epsilon and affine values separately. A matching output shape cannot catch a wrong reduction group.

If validation changes running state, inspect train/eval at the exact call and whether running statistics are tracked. Freezing affine gradients is not a running-buffer policy. If framework means disagree, translate the coefficient algebra before changing tolerances; if means match but variances disagree, inspect the estimators and initialization. If a sequence leaks future information despite a correct attention mask, test normalization with a future-token perturbation. If a constant row is not zero after LayerNorm, inspect its learned beta before declaring the epsilon guard broken.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Running statistic, Momentum convention, Batch coupling using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-017` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 BatchNorm1d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BatchNorm1d.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Why can BatchNorm predictions depend on batch neighbors?**

In training mode, the mean and variance are computed across batch observations. Changing a neighbor changes those shared statistics.

**Why state buffers rather than just weights must be saved?**

Running statistics and batch counter affect future inference even when all trainable parameters are the same. A weights-only mental model misses that state.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-018, BatchNorm, LayerNorm and stateful normalization.
Read courses/deep-learning-pytorch/guides/torch-018.md and courses/deep-learning-pytorch/lessons/torch-018.py. Direct prerequisites: `torch-017`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
