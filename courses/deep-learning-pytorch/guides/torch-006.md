# torch-006: Autograd graphs, the chain rule and in-place hazards

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-005`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Trace a chain-rule derivative through an autograd graph and recognize the two in-place mutations that autograd refuses.

Central investigation: Backpropagate loss = (a-1)**2 with a = z*z and z = 2w at w = 1, check it numerically and mutate a leaf and a saved tensor.

Finish condition: The trace gives z = 2, a = 4, loss 9 and gradient 48, a central difference agrees within 1e-5, and both the leaf mutation and the saved-tensor mutation raise RuntimeError.

The worked examples demonstrate the mechanism; exercises 1-3 transfer it to new inputs and exercises 4-6 extend it to failures and boundary cases. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Autograd follows the chain of tensor operations from a scalar objective back to its inputs. Forz=2w, \(a={z}^{2}\), \(\mathrm{loss}={\left(a-1\right)}^{2}\), the derivative multiplies the local sensitivities along that chain. PyTorch builds the graph dynamically during the forward pass and saves values needed for backward. An in-place mutation can invalidate those saved values, so the framework uses version checks and restricts some mutations. A failure is a signal to understand ownership and graph lifetime, not a reason to bypass checks with .data.

Graph state is also temporary. After a normal backward pass, the saved intermediates are released; reusing the same graph for another backward usually requires an explicit retention policy or a fresh forward computation. Most training loops should recompute the forward graph per batch. Nonlinearities such as ReLU introduce points where a derivative convention matters.

## Design decisions and when to use this method

Use an explicit intermediate trace when introducing a new differentiable operation, debugging a custom backward rule or comparing two implementations with matching forward values. A small scalar chain lets every local factor be checked independently before the same reasoning is applied to vectors and matrices.

Prefer a fresh forward graph for each ordinary training iteration. Retain a graph only when a deliberate algorithm needs repeated derivative queries from the same unchanged forward computation. Treat in-place mutation as a state-ownership decision, not an automatic memory optimization. Use documented update and copying boundaries rather than bypassing autograd safeguards with `.data`.

## Paired TensorFlow comparison

Compare [tf-006](../../deep-learning-tensorflow/guides/tf-006.md) after deriving the shared numerical contract.

TensorFlow records a chosen tape scope, while PyTorch dynamically tracks operations involving requires_grad values. Both need the forward dependencies. PyTorch shared storage and in-place operations make saved-tensor versioning an especially visible debugging concern; avoid translating every TensorFlow assignment into an arbitrary PyTorch in-place edit.

## Vocabulary and concepts

**Autograd graph:** The recorded tensor-operation dependencies used for differentiation.

**Saved tensor:** An intermediate value retained because backward needs it.

**In-place hazard:** A mutation that changes data required by a recorded derivative.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-006`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-006.py` under `.learning/expansion/torch-006/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Build every intermediate from a requires_grad leaf. autograd.grad(loss, w) composes the chain rule. A direct in-place add on a leaf requiring gradients raises RuntimeError unless performed under a deliberate no_grad update context. Mutating a saved input under no_grad can still make a later backward fail its version check. Use clone when a separate mutable value is needed and recompute the graph after optimizer updates.

## Trace the graph and its saved values

The chain is w→z→a→L, with z=2w, \(a={z}^{2}\) and \(L={\left(a-1\right)}^{2}\). At \(w=1\), the full trace is:

| Operation | Forward value | Immediate derivative |
| --- | --- | --- |
| z=2w | \(z=2\) | \(\frac{\partial z}{\partial w}=2\) |
| \(a={z}^{2}\) | \(a=4\) | da/dz=2z=4 |
| \(L={\left(a-1\right)}^{2}\) | \(L=9\) | dL/da=2(a-1)=6 |

Backward composes sensitivities in reverse dependency order: \(\frac{\partial L}{\partial w}=6\cdot 4\cdot 2=48\). Omitting the inner scale gives 24, even though every forward value remains correct. Changing the inner scale to three gives \(z=3\), \(a=9\), \(L=64\) and derivative \(16\cdot 6\cdot 3=288\). A learning-rate adjustment that hides the missing factor for scale 2 would not repair the algorithm for scale 3.

The scalar expression can also be expanded to \(L=16w^4-8w^2+1\). Its derivative \(64w^3-16w\) equals 48 at one, providing a symbolic check independent of the local-factor table. The finite-difference check recomputes the complete expression at 1+h and 1-h. Holding \(a=4\) fixed while perturbing w would instead probe a constant function with slope zero. Equal forward values at one point do not establish equal dependencies.

For larger tensors, reverse-mode differentiation propagates vector-Jacobian products rather than materializing every possible derivative matrix. A scalar loss supplies the initial sensitivity one; each operation transforms the incoming sensitivity using its saved forward values. This explains why the graph must retain information from the actual forward pass and why asking for derivatives of a nonscalar result requires an explicit upstream-gradient convention.

Consider `objective = value.square()` when value is two. Backward needs the original value to produce derivative four. If code then changes that storage to three before calling backward, the old objective still represents the forward value four, but the saved input has changed. Computing derivative six from the new storage would mix two different states. PyTorch's saved-tensor version checks reject such an invalid sequence rather than silently returning that mixed-state result. [PyTorch 2.9 autograd mechanics](https://docs.pytorch.org/docs/2.9/notes/autograd.html).

Using no_grad around the mutation prevents recording that new operation. It does not restore the saved value or make the earlier graph consistent. A safe ordinary update sequence completes the current derivative computation, updates parameter state at a deliberate boundary, then recomputes the next forward graph. Clone can provide separate mutable storage, but a clone is not a substitute for knowing which value each graph depends on.

After a normal derivative computation, saved intermediates can be released. Keeping a reference to loss does not promise another backward pass can reconstruct those released values. Repeated training usually needs a new forward pass, whereas an algorithm intentionally querying multiple derivatives can request graph retention and accept its memory cost. Do not confuse retaining a graph with accumulating gradients across distinct fresh graphs.

ReLU adds a separate mathematical boundary. At a negative input the derivative is zero; at a positive input it is one. At zero there is no unique classical derivative, and PyTorch chooses zero for backward. The numerical convention is not a graph-disconnection error. It should be recorded explicitly when designing derivative tests rather than judged against a symmetric probe's 0.5 as if both were the same object.

## Worked example / walkthrough

### Example A: Trace the chain rule

The factors are dL/da=2(a-1)=6, da/dz=2z=4 and \(\frac{\partial z}{\partial w}=2\). Multiplying \(6\cdot 4\cdot 2\) gives 48 at the supplied point.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w = torch.tensor(1.0, dtype=torch.float64, requires_grad=True)
z = 2 * w
a = z * z
loss = (a - 1) ** 2
gradient = torch.autograd.grad(loss, w)[0]
assert (z.item(), a.item(), loss.item(), gradient.item()) == (2.0, 4.0, 9.0, 48.0)
```

**Expected:** z = 2, a = 4, loss 9, gradient 48.

### Example B: Check an independent slope

The finite difference treats the entire function as a black box. It can expose an incorrect manual chain factor without reading the graph internals.

```python
h = 1e-5
f = lambda value: ((2 * value) ** 2 - 1) ** 2
numeric = (f(1 + h) - f(1 - h)) / (2 * h)
np.testing.assert_allclose(numeric, 48, atol=1e-5, rtol=0)
```

**Expected:** approximately 48 within 1e-5.

### Example C: Observe a leaf mutation guard

The guard prevents an ambiguous modification of a value whose derivative history is being tracked. Optimizer updates use a deliberate state-update boundary instead.

```python
leaf = torch.tensor(1.0, requires_grad=True)
try:
    leaf.add_(1)
except RuntimeError:
    pass
else:
    raise AssertionError("unsafe leaf mutation accepted")
```

**Expected:** RuntimeError.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Trace the chain rule. Predict exercise 6, Recompute after an update, from its prompt alone: Update a scalar under no_grad, then build a fresh quadratic objective and request its derivative. Then explain why this finish condition holds: The trace gives z = 2, a = 4, loss 9 and gradient 48, a central difference agrees within 1e-5, and both the leaf mutation and the saved-tensor mutation raise RuntimeError. Keep each prediction beside the observed value.

## Exercises

1. **Trace the chain at a new point.** Use w=2, \(z=2\cdot w\), \(a=z\cdot z\) and \(\mathrm{loss}={\left(a-1\right)}^{2}\), and predict each intermediate value and dloss/dw.
   **Expected:** z = 4, a = 16, loss 225, gradient 480.
   **Verify:** In a fresh process, the exercise checks confirm `(z2.item(), a2.item(), loss2.item()) == (4.0, 16.0, 225.0)` and `torch.autograd.grad(loss2, w2)[0].item() == 480`.

2. **Check the new slope numerically.** Compare 480 with a central difference of ((2w)**2-1)**2 at w=2 using h=1e-5.
   **Expected:** the central difference agrees with 480 within 1e-6.
   **Verify:** In a fresh process, the exercise checks confirm `(quartic(2 + step) - quartic(2 - step)) / (2 * step)` matches `480` within 1e-06.

3. **Update a leaf under no_grad.** Repeat the in-place add on a leaf that requires gradients, but inside torch.no_grad().
   **Expected:** the update succeeds; the value is 2 and the tensor is still a leaf that requires gradients.
   **Verify:** In a fresh process, the exercise checks confirm `guarded.item() == 2`, `guarded.requires_grad` and `guarded.is_leaf`.

4. **Expose saved-value invalidation.** Build \(\mathrm{loss}=x\cdot x\), mutate x under no_grad before backward, and inspect the failure.
   **Expected:** RuntimeError from a changed saved tensor version.
   **Verify:** In a fresh process, the exercise checks confirm `objective.backward()` raises `RuntimeError`.

5. **Inspect a ReLU convention.** Differentiate ReLU at negative, zero and positive inputs.
   **Expected:** gradients 0, 0, 1.
   **Verify:** In a fresh process, the exercise checks confirm `points.grad` matches `torch.tensor([0.0, 0.0, 1.0])`.

6. **Recompute after an update.** Update a scalar under no_grad, then build a fresh quadratic objective and request its derivative.
   **Expected:** at new \(w=1.5\), gradient -1 for \({\left(w-2\right)}^{2}\).
   **Verify:** In a fresh process, the exercise checks confirm `torch.autograd.grad(fresh, parameter)[0].item() == -1`.

## Common pitfalls and diagnosis

For a factor mismatch, inspect the local derivative table before changing a learning rate. For a zero finite difference, ensure the complete function is recomputed at each perturbed input. For a tensor-version error, locate the first in-place write to a value saved by the forward graph, including writes through an alias or a no_grad block.

A leaf-mutation guard and a later saved-value version error describe different failure points. Do not silence either with `.data`; that can replace an informative failure with an incorrect derivative. If a second backward reports released intermediates, decide whether the algorithm needs a fresh forward computation or deliberate graph retention. If an activation derivative disagrees only at a kink, compare one-sided slopes and the documented convention before investigating numerical precision.

## Progressive hints

Hint 1: Example B (Check an independent slope) alters one assumption of Example A (Trace the chain rule). Hint 2: exercise 4, Expose saved-value invalidation, should end at RuntimeError from a changed saved tensor version. Work backward from it. Hint 3: exercise 5, Inspect a ReLU convention, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Observe a leaf mutation guard, from its inputs alone. Predict whether exercise 3, Update a leaf under no_grad, survives one changed input. Then explain Autograd graph, Saved tensor, In-place hazard in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Trace the chain rule) cannot be rebuilt without help, revisit `torch-005` first. Otherwise keep your exercise 2 attempt, Check the new slope numerically, as a regression case alongside a fresh transfer input, then continue along the course plan.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Does no_grad make any mutation safe?**

No. It stops recording new operations, but a mutation can still invalidate values saved by an earlier graph. Update only at a deliberate boundary and recompute the forward pass.

**Why avoid .data as a workaround?**

It can bypass useful autograd safeguards and create silently incorrect derivatives. Understand the graph and use documented no_grad, detach and clone semantics instead.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-006, Autograd graphs, the chain rule and in-place hazards.
Read courses/deep-learning-pytorch/guides/torch-006.md and courses/deep-learning-pytorch/lessons/torch-006.py. Direct prerequisites: `torch-005`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
