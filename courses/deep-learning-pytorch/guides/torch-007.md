# torch-007: Leaf tensors, detach, no_grad and gradient accumulation

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-006`.

## Learning objectives

Explain when PyTorch stores, accumulates, detaches or skips gradients, and clear accumulated gradients before an independent step.

Central investigation: Backpropagate twice into the same leaf at w = 0, detach a shared view, and compare no_grad with eval mode.

Finish condition: The leaf gradient becomes -4 then -8 without clearing and returns to -4 after reset, the detached view shares storage while a detached clone does not, no_grad output has `requires_grad` False, and eval output still requires grad.

## Purpose and mental model

PyTorch distinguishes graph tracking from gradient storage. A leaf tensor is a graph input created by the user or a registered parameter, while intermediate tensors have operation history. backward accumulates gradients into `leaf.grad` by default. Calling backward twice on newly computed losses without clearing gradients adds the contributions. A nonleaf can retain its gradient when retain_grad is requested, but that is a diagnostic choice rather than the default storage policy.

Detach removes a value from its current graph while sharing storage; clone copies storage while preserving a differentiable relationship. no_grad prevents recording operations in its scope. model.eval changes behavior of modules such as Dropout and BatchNorm, but does not disable autograd. These controls solve different problems and should not be used interchangeably.

## Design decisions and when to use this method

Choose each control for its specific purpose. Use backward when the training algorithm accumulates contributions into parameter gradients. Clear those buffers between independent optimizer steps, while retaining them deliberately across correctly scaled microbatches. Use retain_grad only when an intermediate derivative is useful for a bounded diagnostic.

Use detach to stop differentiation through a value, clone to establish independent storage, and their combination when an observation must have both properties. Use eval to select evaluation behavior of stateful or stochastic layers. Use no_grad or inference_mode separately when recording derivatives is unnecessary. These choices should remain explicit because gradient-based explanation can legitimately run a model in evaluation mode.

## Paired TensorFlow comparison

Compare [tf-007](../../deep-learning-tensorflow/guides/tf-007.md) after deriving the shared numerical contract.

TensorFlow tape.gradient normally returns derivative values rather than storing accumulated `leaf.grad` fields. PyTorch backward requires an explicit clearing policy. TensorFlow training argument and PyTorch train/eval control layer behavior; neither should be confused with the gradient-recording scope.

## Vocabulary and concepts

**Leaf tensor:** An input or parameter whose gradient is accumulated by backward.

**Detach:** Removing a value from an existing autograd graph without necessarily copying storage.

**Gradient accumulation:** Adding new backward contributions into an existing grad field.

**Gradient mode:** Whether new operations are recorded for differentiation.

## How to run this lesson

Run `torch-007` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C reuse `w` from earlier blocks; run all three in order.

## Syntax anatomy and reasoning sequence

Set `requires_grad` on floating-point inputs that need derivatives. Use backward for accumulated leaf gradients and `zero_grad(set_to_none=True)` between independent optimizer steps. detached=value.detach() does not allocate independent storage; use value.detach().clone() for an owned logging snapshot. Check is_leaf and grad_fn to understand the graph role rather than guessing from a variable name.

## Separate four kinds of state

A tensor's value, storage aliases, graph role and stored gradient are related but different facts. Module mode adds another independent control:

| Control or observation | What it changes or reports | What it does not establish |
| --- | --- | --- |
| `requires_grad` | Whether relevant operations can be tracked for derivatives | Independent storage or optimizer membership |
| is_leaf and grad_fn | Role in the recorded graph | Whether the Python variable name sounds like a parameter |
| backward | Adds derivative contributions to eligible stored gradients | A parameter update |
| detach | Removes the current differentiation connection | A copy of storage |
| clone | Copies storage | A detached gradient history |
| no_grad | Suppresses recording for ordinary operations in its scope | Evaluation behavior of Dropout or BatchNorm |
| eval | Selects evaluation behavior of affected modules | Disabled autograd or cleared gradients |

For tensors requiring gradients, a leaf is not the result of a tracked differentiable operation. An intermediate such as `2 * w` has an operation history even when assigned to a named variable. Tensors not requiring gradients are treated as leaves by convention. A conversion or copy operation can therefore change the graph role of a tracked tensor; inspect the actual metadata instead of assuming every user-named tensor is a leaf. [PyTorch 2.9 is_leaf](https://docs.pytorch.org/docs/2.9/generated/torch.Tensor.is_leaf.html).

The first fixture has \(w=0\) and intermediate=2w. Backpropagating that scalar gives incoming sensitivity one at the intermediate and sensitivity two at w. The intermediate's gradient is visible only because retain_grad was requested. Its absence by default would be a storage-policy observation, not evidence that the chain rule failed.

Now reset `w.grad` to None and compute (w-2)². The new contribution is -4. Building the same expression again creates a fresh graph, but backward adds another -4 into the existing gradient buffer, leaving -8. A fresh graph does not clear a previous buffer. Resetting to None before the third computation gives -4 again without changing w itself.

None and numeric zero have different meanings. None may indicate that no gradient has been stored, that a reset occurred, that the tensor was unused, or that an intermediate was not retained. A numeric zero can be the correct derivative of a connected path. Optimizers can also treat them differently: parameters with None gradients are commonly skipped, whereas zero gradients may still interact with momentum or weight decay. This distinction is documented for zero_grad rather than being merely a display detail. [PyTorch 2.9 zero_grad](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.zero_grad.html).

The detach example changes shared storage. After detached=source.detach(), writing `detached[0] = 9` changes `source[0]` as well. The earlier source.detach().clone() snapshot remains one because it owns a copy. The snapshot is suitable for comparing later mutation, but detaching a value that the objective actually needs can break learning. Ownership and differentiation must both match the intended interface.

Finally, model.eval() does not stop derivatives through a Linear layer. It changes a module's training flag and the behavior of layers that consult it. no_grad affects ordinary operation recording while leaving the original tensor's `requires_grad` flag unchanged; factory operations with an explicit `requires_grad` argument are a documented exception to treating the scope as a blanket flag rewrite. Keep mode, recording and gradient-buffer decisions separate in the surrounding training or inference function.

## Worked example / walkthrough

### Example A: Inspect leaf and nonleaf state

Leaf status follows graph construction, not whether a tensor is assigned to a Python variable. retain_grad explicitly requests storage for the intermediate diagnostic.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w = torch.tensor(0.0, requires_grad=True)
intermediate = 2 * w
intermediate.retain_grad()
intermediate.backward()
assert (
    w.is_leaf and not intermediate.is_leaf and w.grad.item() == 2 and intermediate.grad.item() == 1
)
```

**Expected:** `w.is_leaf` is `True`; `u.is_leaf` is `False`; the gradients with respect to \(w\) and \(u\) are 2 and 1.

### Example B: Observe accumulation across fresh graphs

The second forward creates a new graph, but backward still adds into the existing leaf gradient buffer. Graph freshness does not imply gradient-buffer freshness.

```python
w.grad = None
((w - 2) ** 2).backward()
assert w.grad.item() == -4
((w - 2) ** 2).backward()
assert w.grad.item() == -8
```

**Expected:** after resetting first, grad -4 then -8.

### Example C: Clear before an independent step

This is the intended reset for independent batches. Intentional microbatch accumulation needs a separate scaling and update policy.

```python
w.grad = None
((w - 2) ** 2).backward()
assert w.grad.item() == -4
```

**Expected:** grad returns to -4.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Inspect leaf and nonleaf state. Predict exercise 6, Show eval is separate, from its prompt alone: Put a Linear module in eval mode, run a differentiable input, and inspect output tracking. Then explain why this finish condition holds: The leaf gradient becomes -4 then -8 without clearing and returns to -4 after reset, the detached view shares storage while a detached clone does not, no_grad output has `requires_grad` False, and eval output still requires grad. Keep each prediction beside the observed value.

## Exercises

1. **Predict a nonleaf gradient.** Create leaf v=1.0 and intermediate u=3v, retain u's gradient and backpropagate u*u.
   **Expected:** u.grad is 6 and v.grad is 18; u is not a leaf.
   **Verify:** In a fresh process, the exercise checks confirm `v.grad.item() == 18`, `u.grad.item() == 6` and `not u.is_leaf`.

2. **Accumulate three backward calls.** At w=1, backpropagate \({\left(w-2\right)}^{2}\) three times without clearing the gradient.
   **Expected:** each call contributes -2, so the stored gradient is -6.
   **Verify:** In a fresh process, the exercise checks confirm `p.grad.item() == -6`.

3. **Clear with zero_ and with None.** Clear the accumulated gradient with p.grad.zero_() and backpropagate once, then set it to None and backpropagate once more.
   **Expected:** both routes end at -2; after the None assignment the gradient is absent until the next backward.
   **Verify:** In a fresh process, the exercise checks confirm `p.grad.item() == -2`, `p.grad is None` and `p.grad.item() == -2`.

4. **Separate detach from ownership.** Detach a tensor, mutate the detached view, and compare with a detached clone.
   **Expected:** shared original changes; owned clone stays unchanged.
   **Verify:** In a fresh process, the exercise checks confirm `source[0].item() == 9`, `owned[0].item() == 1` and `not detached.requires_grad`.

5. **Use no_grad for an observation.** Multiply a `requires_grad` tensor inside and outside no_grad.
   **Expected:** tracked result `requires_grad` True; observed result False.
   **Verify:** In a fresh process, the exercise checks confirm `tracked.requires_grad` and `not observed.requires_grad`.

6. **Show eval is separate.** Put a Linear module in eval mode, run a differentiable input, and inspect output tracking.
   **Expected:** the output still has `requires_grad=True`.
   **Verify:** In a fresh process, the exercise checks confirm `result.requires_grad` and `model.training is False`.

## Common pitfalls and diagnosis

If a gradient doubles across supposedly independent steps, check where zero_grad occurs and whether backward was called twice. If an intermediate's grad is None, inspect is_leaf and whether retain_grad was requested before declaring the path disconnected. If a frozen or unused parameter moves, inspect optimizer state and the difference between a zero gradient and no gradient.

If a saved observation changes later, look for shared storage through detach or a view. If a model in eval mode still creates a graph, that is expected unless gradient recording was separately disabled. If a logging detach unexpectedly stops training, trace whether the detached value was fed back into the loss. These diagnoses require inspecting values, graph connections, buffers and module mode independently rather than replacing every None with zero or adding no_grad around the whole loop.

## Progressive hints

Hint 1: Example B (Observe accumulation across fresh graphs) alters one assumption of Example A (Inspect leaf and nonleaf state). Hint 2: exercise 4, Separate detach from ownership, should end at shared original changes; owned clone stays unchanged. Work backward from it. Hint 3: exercise 5, Use no_grad for an observation, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Clear before an independent step, from its inputs alone. Predict whether exercise 3, Clear with zero_ and with None, survives one changed input. Then explain Leaf tensor, Detach, Gradient accumulation in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Inspect leaf and nonleaf state) cannot be rebuilt without help, revisit `torch-006` first. `torch-008` (One optimizer step you can audit) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22 for the Leaf tensor, Detach, Gradient accumulation behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Why does eval not disable gradients?**

Evaluation behavior and differentiation are independent concerns. Gradient-based analysis may intentionally run a model in evaluation mode while differentiating its outputs.

**When is detach().clone useful?**

When a value should be disconnected from autograd and own storage that later mutations cannot change, such as an immutable comparison snapshot.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-007, Leaf tensors, detach, no_grad and gradient accumulation.
Read courses/deep-learning-pytorch/guides/torch-007.md and courses/deep-learning-pytorch/lessons/torch-007.py. Direct prerequisites: `torch-006`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
