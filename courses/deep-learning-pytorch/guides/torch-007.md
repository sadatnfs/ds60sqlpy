# torch-007: Leaf tensors, detach, no_grad and gradient accumulation

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-006`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

PyTorch distinguishes graph tracking from gradient storage. The central investigation is concrete: Create a leaf tensor \(w=0\) and intermediate tensor \(u=2w\), retain the intermediate gradient and backpropagate its sum. The finish condition is `w.is_leaf` is `True`; `u.is_leaf` is `False`; the gradients with respect to \(w\) and \(u\) are 2 and 1. the output still has `requires_grad=True`. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

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

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-007`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-007.py` under `.learning/expansion/torch-007/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

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

For tensors requiring gradients, a leaf is not the result of a tracked differentiable operation. An intermediate such as 2 w has an operation history even when assigned to a named variable. Tensors not requiring gradients are treated as leaves by convention. A conversion or copy operation can therefore change the graph role of a tracked tensor; inspect the actual metadata instead of assuming every user-named tensor is a leaf. [PyTorch 2.9 is_leaf](https://docs.pytorch.org/docs/2.9/generated/torch.Tensor.is_leaf.html).

The first fixture has \(w=0\) and intermediate=2w. Backpropagating that scalar gives incoming sensitivity one at the intermediate and sensitivity two at w. The intermediate's gradient is visible only because retain_grad was requested. Its absence by default would be a storage-policy observation, not evidence that the chain rule failed.

Now reset `w.grad` to None and compute(w-2)². The new contribution is -4. Building the same expression again creates a fresh graph, but backward adds another -4 into the existing gradient buffer, leaving -8. A fresh graph does not clear a previous buffer. Resetting to None before the third computation gives -4 again without changing w itself.

None and numeric zero have different meanings. None may indicate that no gradient has been stored, that a reset occurred, that the tensor was unused, or that an intermediate was not retained. A numeric zero can be the correct derivative of a connected path. Optimizers can also treat them differently: parameters with None gradients are commonly skipped, whereas zero gradients may still interact with momentum or weight decay. This distinction is documented for zero_grad rather than being merely a display detail. [PyTorch 2.9 zero_grad](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.zero_grad.html).

The detach example changes shared storage. After detached=source.detach(), writing detached[0]=9 changes source[0] as well. The earlier source.detach().clone() snapshot remains one because it owns a copy. The snapshot is suitable for comparing later mutation, but detaching a value that the objective actually needs can break learning. Ownership and differentiation must both match the intended interface.

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

**Expected:** grad returns to-4.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: `w.is_leaf` is `True`; `u.is_leaf` is `False`; the gradients with respect to \(w\) and \(u\) are 2 and 1. the output still has `requires_grad=True`. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect leaf and nonleaf state.** Create a leaf tensor \(w=0\) and intermediate tensor \(u=2w\), retain the intermediate gradient and backpropagate its sum.
   **Expected:** `w.is_leaf` is `True`; `u.is_leaf` is `False`; the gradients with respect to \(w\) and \(u\) are 2 and 1.
   **Verify:** Save the assertion results for exercise 1, including `w.is_leaf` is `True`; `u.is_leaf` is `False`; the gradients with respect to \(w\) and \(u\) are 2 and 1.

2. **Observe accumulation across fresh graphs.** Compute \({\left(w-2\right)}^{2}\) twice at \(w=0\) without clearing grad.
   **Expected:** after resetting first, grad -4 then -8.
   **Verify:** Save the assertion results for exercise 2, including after resetting first, grad -4 then -8.

3. **Clear before an independent step.** Set grad None and backpropagate once more.
   **Expected:** grad returns to-4.
   **Verify:** Save the assertion results for exercise 3, including grad returns to-4.

4. **Separate detach from ownership.** Detach a tensor, mutate the detached view, and compare with a detached clone.
   **Expected:** shared original changes; owned clone stays unchanged.
   **Verify:** Save the assertion results for exercise 4, including shared original changes; owned clone stays unchanged.

5. **Use no_grad for an observation.** Multiply a `requires_grad` tensor inside and outside no_grad.
   **Expected:** tracked result `requires_grad` True; observed result False.
   **Verify:** Save the assertion results for exercise 5, including tracked result `requires_grad` True; observed result False.

6. **Show eval is separate.** Put a Linear module in eval mode, run a differentiable input, and inspect output tracking.
   **Expected:** the output still has `requires_grad=True`.
   **Verify:** Save the assertion results for exercise 6, including the output still has `requires_grad=True`.

## Common pitfalls and diagnosis

If a gradient doubles across supposedly independent steps, check where zero_grad occurs and whether backward was called twice. If an intermediate's grad is None, inspect is_leaf and whether retain_grad was requested before declaring the path disconnected. If a frozen or unused parameter moves, inspect optimizer state and the difference between a zero gradient and no gradient.

If a saved observation changes later, look for shared storage through detach or a view. If a model in eval mode still creates a graph, that is expected unless gradient recording was separately disabled. If a logging detach unexpectedly stops training, trace whether the detached value was fed back into the loss. These diagnoses require inspecting values, graph connections, buffers and module mode independently rather than replacing every None with zero or adding no_grad around the whole loop.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Leaf tensor, Detach, Gradient accumulation using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-006` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

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
