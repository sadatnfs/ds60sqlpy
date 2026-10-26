# torch-027: Transfer learning, frozen layers and optimizer membership

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-026`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Transfer learning reuses a representation while adapting a task-specific head. The central investigation is concrete: Create a bias-free 2-to-2 identity Linear base and disable its parameter gradients. The finish condition is base output equals input; all base parameters frozen. base weight now changes. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Transfer learning reuses a representation while adapting a task-specific head. Freezing requires both a gradient policy and a correct optimizer membership policy. Setting `requires_grad=False` prevents new derivatives for those parameters, but an optimizer can still contain stale gradient state if the transition is handled carelessly. Clear old gradients and deliberately select trainable parameters. Evaluation mode is a separate concern: a frozen BatchNorm base can still update running buffers if left in training mode.

The local fixture uses a fixed identity base and a new linear head, so a byte-level snapshot can verify that only the head changes. A later unfreeze phase creates a new optimizer with a declared rate and membership list. No pretrained weights are downloaded. The lesson teaches the state transition required for transfer rather than claiming that freezing always improves quality.

## Design decisions and when to use this method

Freeze a base when reusing its current representation is a deliberate adaptation strategy, and define whether its running buffers and stochastic behavior must remain fixed too. Separate `requires_grad`, optimizer membership, stored gradients and train/eval mode. None of those controls alone proves the complete freeze contract.

Treat unfreezing as a new training phase with a stated learning rate, parameter set and optimizer-state policy. Creating a fresh optimizer is the simple policy used here. Adding a reviewed parameter group to an existing optimizer is another supported choice when preserving prior head state is intended; it should not happen implicitly.

## Paired TensorFlow comparison

Compare [tf-027](../../deep-learning-tensorflow/guides/tf-027.md) after deriving the shared numerical contract.

Keras trainable flags and the training argument interact with layer tracking and mode behavior; PyTorch separates `requires_grad`, optimizer lists and train/eval. In both frameworks, freezing parameters does not automatically establish that every stateful forward behavior is frozen.

## Vocabulary and concepts

**Frozen base:** A reused model component excluded from parameter updates.

**Optimizer membership:** The exact parameters supplied to an optimizer.

**Mode-dependent buffer:** State that can change during forward even without parameter gradients.

**Unfreeze phase:** A deliberate transition to updating previously frozen state.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-027`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-027.py` under `.learning/expansion/torch-027/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Call requires_grad_(False) on base parameters, clear their grad fields, and construct the head optimizer from head.parameters only. Use base.eval when its mode-dependent state should remain fixed. Snapshot all base state_dict tensors with clone. After training the head, compare both parameters and buffers. Unfreezing changes the intended update set and requires an explicit optimizer policy.

## Trace what freezing preserves and what it does not

The base is a bias-free 2-to-2 Linear layer initialized to identity. Its stored weight has shape(2, 2), and base(x)=x for the three fixture rows. The head has shape(1, 2) and begins at zero. Disabling base parameter gradients and supplying only head.parameters() to SGD establishes two distinct boundaries: the base does not receive new parameter derivatives, and the optimizer is not asked to update it.

The head update has an independent analytic value. With targets[1, 2, 3], zero predictions and mean squared error, the residuals are[-1, -2, -3]. The head gradient is(2/3) times the feature-weighted residual sum, namely[-8/3, -10/3]. SGD at 0.1 produces head weights[4/15, \(\frac{1}{3}\)] and predictions[4/15, \(\frac{1}{3}\), 3/5]. This explains both the observed nonzero head update and why the base need not change for the head to learn.

When the base is later unfrozen, the derivative path through it becomes relevant. If its stored weight is B and the head row is h, features are \(XB^{\mathsf T}\) and logits are \(XB^{\mathsf T}h^{\mathsf T}\). The base gradient combines the output residuals with h and X. After the head has nonzero weights, that gradient can be nonzero. Enabling `requires_grad` does not add B to an optimizer that was constructed from head parameters only. The update set must be changed deliberately.

A parameter can remain in an optimizer after `requires_grad` becomes false. That flag prevents new gradient construction for the leaf, but it does not erase an old `.grad` tensor. An optimizer step using that stale tensor can still change the parameter. Clear stored gradients at the phase boundary and inspect the exact optimizer-held objects. For the supplied built-in update policy, `grad=None` skips the corresponding update; an allocated zero gradient and a missing gradient are not interchangeable in every state/decay situation.

Freezing parameters is also different from wrapping computation in no_grad. If a trainable upstream adapter needs gradients through a fixed base, its input derivative must remain connected even though base parameters are frozen. no_grad around the whole base would sever that upstream path. Conversely, when features are truly fixed and no earlier component is trained, avoiding unnecessary graph construction can be an intentional efficiency choice. State the intended gradient destination first.

Mode-dependent buffers form another axis. BatchNorm affine weights can be frozen while training-mode forward still updates running mean, running variance and batch counters. Dropout can remain stochastic without any trainable parameter of its own. base.eval() changes those module behaviors; it does not disable autograd or alter optimizer membership. A later parent_model.train() can recursively put the base back into training mode, so the intended fixed-mode policy must be restored or encoded deliberately in the training procedure.

A freeze receipt should compare the complete intended tensor state, not just the Linear weight. Clone the relevant state_dict tensors before the phase so the snapshot does not alias later mutations. Record mode flags separately because they are not ordinary learned tensors in state_dict. The tiny Linear base has no running statistics, while the separate BatchNorm exercise makes this hidden-state issue observable.

At unfreeze, there are two different optimizer-state policies. A new optimizer resets momentum/adaptive state for the head as well as introducing the base, which changes the trajectory. add_param_group can preserve existing head state while adding previously excluded parameters with explicit group options. It requires avoiding duplicate membership and deciding rates, decay and scheduler behavior for the new group. The API supports this use, but the resulting experiment still needs its own state receipt. [PyTorch 2.9 add_param_group](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.add_param_group.html).

The paired Keras guide uses trainable flags and a deliberate training argument for the base. Those mechanisms are not a one-to-one spelling substitution for PyTorch `requires_grad`, optimizer lists and train/eval. In either framework, verify before/after tensors, buffer behavior and actual updated identities. The local identity base is a controlled ownership fixture, not a downloaded pretrained model or evidence that transfer will improve an unseen task.

## Worked example / walkthrough

### Example A: Freeze a known base

The identity fixture isolates ownership. A learned base would have different values but should obey the same freeze contract.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

base=nn.Linear(2,2,bias=False)
with torch.no_grad(): base.weight.copy_(torch.eye(2))
for parameter in base.parameters(): parameter.requires_grad_(False); parameter.grad=None
x=torch.tensor([[1.,0.],[0.,1.],[1.,1.]])
assert torch.equal(base(x),x) and not any(p.requires_grad for p in base.parameters())
```

**Expected:** base output equals input; all base parameters frozen.

### Example B: Train a new head

The optimizer receives only head parameters. The direct snapshot check proves preservation rather than trusting a flag alone.

```python
head=nn.Linear(2,1,bias=False)
with torch.no_grad(): head.weight.zero_()
base_before=base.weight.detach().clone(); head_before=head.weight.detach().clone(); target=torch.tensor([[1.],[2.],[3.]])
optimizer=torch.optim.SGD(head.parameters(),lr=.1); optimizer.zero_grad(set_to_none=True); loss=(head(base(x))-target).square().mean(); loss.backward(); optimizer.step()
assert not torch.equal(head.weight,head_before) and torch.equal(base.weight,base_before)
```

**Expected:** head changes; base remains exact identity.

### Example C: Inspect absent base gradients

The head can learn from fixed features without differentiating base parameters. This is a computation path with a deliberate gradient boundary.

```python
assert base.weight.grad is None and head.weight.grad is not None
```

**Expected:** base gradient None; head gradient present.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: base output equals input; all base parameters frozen. base weight now changes. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Freeze a known base.** Create a bias-free 2-to-2 identity Linear base and disable its parameter gradients.
   **Expected:** base output equals input; all base parameters frozen.
   **Verify:** Save the assertion results for exercise 1, including base output equals input; all base parameters frozen.

2. **Train a new head.** Attach a zero-initialized 2-to-1head and take one SGD.1step toward targets 1, 2, 3.
   **Expected:** head changes; base remains exact identity.
   **Verify:** Save the assertion results for exercise 2, including head changes; base remains exact identity.

3. **Inspect absent base gradients.** Check the frozen base after head backward.
   **Expected:** base gradient None; head gradient present.
   **Verify:** Save the assertion results for exercise 3, including base gradient None; head gradient present.

4. **Expose buffer updates despite freezing.** Freeze BatchNorm affine parameters but call it in train mode on a nonzero batch.
   **Expected:** running mean changes.
   **Verify:** Save the assertion results for exercise 4, including running mean changes.

5. **Freeze normalization behavior with eval.** Switch that BatchNorm to eval and call a different batch.
   **Expected:** running mean remains unchanged.
   **Verify:** Save the assertion results for exercise 5, including running mean remains unchanged.

6. **Begin an explicit unfreeze phase.** Enable base gradients, create a new optimizer over base+head, and take one smaller-rate step.
   **Expected:** base weight now changes.
   **Verify:** Save the assertion results for exercise 6, including base weight now changes.

## Common pitfalls and diagnosis

If a supposedly frozen weight changes, inspect stale .grad values, optimizer membership, decay and explicit in-place writes. If weights stay fixed but predictions drift, inspect running buffers and stochastic training mode. If an unfrozen parameter gets a gradient but does not move, check whether the current optimizer contains that exact object.

If upstream adaptation stops learning after freezing the base, look for a broad no_grad/detach boundary that removed the needed input derivative. If an unfreeze run differs from continuation, compare the chosen optimizer reset versus retained-state policy before blaming the learning rate. A snapshot that shares storage with the current model cannot prove preservation; clone it and test a controlled changed tensor.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Frozen base, Optimizer membership, Mode-dependent buffer using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-026` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Can frozen parameters still leave a drifting model?**

Yes. Running statistics and other buffers may update in training mode. Compare the complete intended state, not only trainable weights.

**Why recreate an optimizer on unfreeze?**

It makes the new parameter membership and optimizer-state policy explicit. An existing optimizer does not automatically discover newly enabled or replaced parameters.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-027, Transfer learning, frozen layers and optimizer membership.
Read courses/deep-learning-pytorch/guides/torch-027.md and courses/deep-learning-pytorch/lessons/torch-027.py. Direct prerequisites: `torch-026`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
