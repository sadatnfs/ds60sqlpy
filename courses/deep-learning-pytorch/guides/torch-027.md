# torch-027: Transfer learning, frozen layers and optimizer membership

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-026`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Transfer learning reuses a representation while adapting a task-specific head. The central investigation is concrete: Create a bias-free2-to-2 identity Linear base and disable its parameter gradients. The finish condition is base output equals input; all base parameters frozen. base weight now changes. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Transfer learning reuses a representation while adapting a task-specific head. Freezing requires both a gradient policy and a correct optimizer membership policy. Setting requires_grad=False prevents new derivatives for those parameters, but an optimizer can still contain stale gradient state if the transition is handled care lessly. Clear old gradients and deliberately select trainable parameters. Evaluation mode is a separate concern: a frozen BatchNorm base can still update running buffers if left in training mode.

The local fixture uses a fixed identity base and a new linear head, so a byte-level snapshot can verify that only the head changes. A later unfreeze phase creates a new optimizer with a declared rate and membership list. No pretrained weights are downloaded. The lesson teaches the state transition required for transfer rather than claiming that freezing always improves quality.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-027](../../deep-learning-tensorflow/guides/tf-027.md) after deriving the shared numerical contract.

Keras trainable flags and the training argument interact with layer tracking and mode behavior; PyTorch separates requires_grad, optimizer lists and train/eval. In both frameworks, freezing parameters does not automatically establish that every stateful forward behavior is frozen.

## Vocabulary and concepts

**Frozen base:** A reused model component excluded from parameter updates.

**Optimizer membership:** The exact parameters supplied to an optimizer.

**Mode-dependent buffer:** State that can change during forward even without parameter gradients.

**Unfreeze phase:** A deliberate transition to updating previously frozen state.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-027/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-027.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-027.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Call requires_grad_(False) on base parameters, clear their grad fields, and construct the head optimizer from head.parameters only. Use base.eval when its mode-dependent state should remain fixed. Snapshot all base state_dict tensors with clone. After training the head, compare both parameters and buffers. Unfreezing changes the intended update set and requires an explicit optimizer policy.

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

1. **Freeze a known base.** Create a bias-free2-to-2 identity Linear base and disable its parameter gradients.
   **Expected:** base output equals input; all base parameters frozen.
   **Verify:** Save the assertion results for exercise 1, including base output equals input; all base parameters frozen.

2. **Train a new head.** Attach a zero-initialized2-to-1 head and take one SGD.1 step toward targets1, 2, 3.
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

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Frozen base, Optimizer membership, Mode-dependent buffer using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-026` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Can frozen parameters still leave a drifting model?**

Yes. Running statistics and other buffers may update in training mode. Compare the complete intended state, not only trainable weights.

**Why recreate an optimizer on unfreeze?**

It makes the new parameter membership and optimizer-state policy explicit. An existing optimizer does not automatically discover newly enabled or replaced parameters.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-027, Transfer learning, frozen layers and optimizer membership.
Read courses/deep-learning-pytorch/guides/torch-027.md and courses/deep-learning-pytorch/lessons/torch-027.py. Direct prerequisites: `torch-026`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
