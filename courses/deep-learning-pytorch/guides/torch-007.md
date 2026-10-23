# torch-007: Leaf tensors, detach, no_grad and gradient accumulation

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-006`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

PyTorch distinguishes graph tracking from gradient storage. The central investigation is concrete: Create leaf w0 and intermediate2 w, retain the intermediate gradient and backpropagate its sum. The finish condition is w leaf True; intermediate False; gradients2 and1. output still requires_grad True. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

PyTorch distinguishes graph tracking from gradient storage. A leaf tensor is a graph input created by the user or a registered parameter, while intermediate tensors have operation history. backward accumulates gradients into leaf.grad by default. Calling backward twice on newly computed losses without clearing gradients adds the contributions. A nonleaf can retain its gradient when retain_grad is requested, but that is a diagnostic choice rather than the default storage policy.

Detach removes a value from its current graph while sharing storage; clone copies storage while preserving a differentiable relationship. no_grad prevents recording operations in its scope. model.eval changes behavior of modules such as Dropout and BatchNorm, but does not disable autograd. These controls solve different problems and should not be used interchangeably.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-007](../../deep-learning-tensorflow/guides/tf-007.md) after deriving the shared numerical contract.

TensorFlow tape.gradient normally returns derivative values rather than storing accumulated leaf.grad fields. PyTorch backward requires an explicit clearing policy. TensorFlow training argument and PyTorch train/eval control layer behavior; neither should be confused with the gradient-recording scope.

## Vocabulary and concepts

**Leaf tensor:** An input or parameter whose gradient is accumulated by backward.

**Detach:** Removing a value from an existing autograd graph without necessarily copying storage.

**Gradient accumulation:** Adding new backward contributions into an existing grad field.

**Gradient mode:** Whether new operations are recorded for differentiation.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-007/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-007.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-007.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Set requires_grad on floating-point inputs that need derivatives. Use backward for accumulated leaf gradients and zero_grad(set_to_none=True) between independent optimizer steps. detached=value.detach() does not allocate independent storage; use value.detach().clone() for an owned logging snapshot. Check is_leaf and grad_fn to understand the graph role rather than guessing from a variable name.

## Worked example / walkthrough

### Example A: Inspect leaf and nonleaf state

Leaf status follows graph construction, not whether a tensor is assigned to a Python variable. retain_grad explicitly requests storage for the intermediate diagnostic.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w=torch.tensor(0.,requires_grad=True); intermediate=2*w; intermediate.retain_grad(); intermediate.backward()
assert w.is_leaf and not intermediate.is_leaf and w.grad.item()==2 and intermediate.grad.item()==1
```

**Expected:** w leaf True; intermediate False; gradients2 and1.

### Example B: Observe accumulation across fresh graphs

The second forward creates a new graph, but backward still adds into the existing leaf gradient buffer. Graph freshness does not imply gradient-buffer freshness.

```python
w.grad=None; ((w-2)**2).backward(); assert w.grad.item()==-4
((w-2)**2).backward(); assert w.grad.item()==-8
```

**Expected:** after resetting first, grad -4 then -8.

### Example C: Clear before an independent step

This is the intended reset for independent batches. Intentional microbatch accumulation needs a separate scaling and update policy.

```python
w.grad=None; ((w-2)**2).backward(); assert w.grad.item()==-4
```

**Expected:** grad returns to-4.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: w leaf True; intermediate False; gradients2 and1. output still requires_grad True. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect leaf and nonleaf state.** Create leaf w0 and intermediate2 w, retain the intermediate gradient and backpropagate its sum.
   **Expected:** w leaf True; intermediate False; gradients2 and1.
   **Verify:** Save the assertion results for exercise 1, including w leaf True; intermediate False; gradients2 and1.

2. **Observe accumulation across fresh graphs.** Compute (w-2)**2 twice at w=0 without clearing grad.
   **Expected:** after resetting first, grad -4 then -8.
   **Verify:** Save the assertion results for exercise 2, including after resetting first, grad -4 then -8.

3. **Clear before an independent step.** Set grad None and backpropagate once more.
   **Expected:** grad returns to-4.
   **Verify:** Save the assertion results for exercise 3, including grad returns to-4.

4. **Separate detach from ownership.** Detach a tensor, mutate the detached view, and compare with a detached clone.
   **Expected:** shared original changes; owned clone stays unchanged.
   **Verify:** Save the assertion results for exercise 4, including shared original changes; owned clone stays unchanged.

5. **Use no_grad for an observation.** Multiply a requires_grad tensor inside and outside no_grad.
   **Expected:** tracked result requires_grad True; observed result False.
   **Verify:** Save the assertion results for exercise 5, including tracked result requires_grad True; observed result False.

6. **Show eval is separate.** Put a Linear module in eval mode, run a differentiable input, and inspect output tracking.
   **Expected:** output still requires_grad True.
   **Verify:** Save the assertion results for exercise 6, including output still requires_grad True.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Leaf tensor, Detach, Gradient accumulation using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-006` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why does eval not disable gradients?**

Evaluation behavior and differentiation are independent concerns. Gradient-based analysis may intentionally run a model in evaluation mode while differentiating its outputs.

**When is detach().clone useful?**

When a value should be disconnected from autograd and own storage that later mutations cannot change, such as an immutable comparison snapshot.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-007, Leaf tensors, detach, no_grad and gradient accumulation.
Read courses/deep-learning-pytorch/guides/torch-007.md and courses/deep-learning-pytorch/lessons/torch-007.py. Direct prerequisites: `torch-006`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
