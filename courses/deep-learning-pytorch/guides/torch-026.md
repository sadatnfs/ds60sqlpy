# torch-026: Custom modules, residual paths, buffers and autograd checks

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-025`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Custom modules should make state ownership and differentiation explicit. The central investigation is concrete: Create a width2 residual with zero kernel and scale buffer1. The finish condition is output equals input; one parameter and one buffer. gradient24. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Custom modules should make state ownership and differentiation explicit. Parameters are optimized; buffers are tracked but normally fixed; temporary activations are rebuilt during forward. A residual branch adds a transformed input to the original, so feature dimensions must match or an explicit projection must reconcile them. Creating new parameters in forward would change model identity and invalidate optimizer membership.

A custom differentiable function should be checked against independent derivatives before being trusted in a large network. PyTorch grad check uses finite differences, usually with float64 inputs, to compare a backward formula with the numerical behavior of forward. Passing a few checks is useful evidence under those inputs, not a proof for every branch or nondifferentiable point. This lesson combines a simple residual module with a tiny custom cube function so both registration and derivative contracts remain inspectable.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-026](../../deep-learning-tensorflow/guides/tf-026.md) after deriving the shared numerical contract.

Keras custom layers often create weights in build and define call; PyTorch modules usually register state in __init__ and define forward. TensorFlow custom-gradient mechanisms and PyTorch autograd.Function both require a correct local derivative multiplied by the incoming gradient.

## Vocabulary and concepts

**Custom module:** A reusable computation with explicitly registered state.

**Buffer:** Tracked tensor state outside the optimizer parameter set.

**Grad check:** A numerical comparison of a backward rule with finite differences.

**Incoming gradient:** The derivative from later operations supplied to a local backward rule.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-026/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-026.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-026.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Assign nn.Parameter in __init__, register a scale buffer, and implement forward without allocating new trainable state. Use named_parameters and named_buffers to inspect ownership. A torch.autograd.Function defines static forward and backward methods; save_for_backward stores inputs needed later. grad check perturbs double-precision inputs and should avoid kinks. The cube derivative is3*x² times the incoming gradient.

## Worked example / walkthrough

### Example A: Build an identity residual

A zero branch makes the initial residual an exact identity. The branch can still receive gradients because its input is nonzero.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
class Residual(nn.Module):
    def __init__(self,width):
        super().__init__(); self.width=width; self.kernel=nn.Parameter(torch.zeros((width,width),dtype=torch.float64)); self.register_buffer('scale',torch.tensor(1.,dtype=torch.float64))
    def forward(self,x):
        if x.ndim!=2 or x.shape[1]!=self.width: raise ValueError('feature width mismatch')
        return x+self.scale*(x@self.kernel)
class Cube(torch.autograd.Function):
    @staticmethod
    def forward(ctx,x): ctx.save_for_backward(x); return x**3
    @staticmethod
    def backward(ctx,grad_output):
        (x,)=ctx.saved_tensors; return grad_output*3*x*x
module=Residual(2); x=torch.tensor([[1.,2.],[3.,4.]],dtype=torch.float64)
assert torch.equal(module(x),x)
assert set(dict(module.named_parameters()))=={'kernel'} and set(dict(module.named_buffers()))=={'scale'}
```

**Expected:** output equals input; one parameter and one buffer.

### Example B: Keep state stable across calls

Batch length changes transient activations, not the number of learned coefficients. Stable state is necessary for optimizer and checkpoint consistency.

```python
identity=id(module.kernel); module(torch.ones((1,2),dtype=torch.float64))
assert id(module.kernel)==identity and sum(p.numel() for p in module.parameters())==4
```

**Expected:** same kernel object and parameter count 4.

### Example C: Check a known residual transform

The buffer changes forward behavior while remaining outside the trainable parameter list. It therefore belongs in the serialized state contract.

```python
with torch.no_grad(): module.kernel.copy_(torch.eye(2,dtype=torch.float64)); module.scale.fill_(.5)
torch.testing.assert_close(module(x),1.5*x,atol=1e-12,rtol=0)
```

**Expected:** output1.5*x.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: output equals input; one parameter and one buffer. gradient24. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Build an identity residual.** Create a width2 residual with zero kernel and scale buffer1.
   **Expected:** output equals input; one parameter and one buffer.
   **Verify:** Save the assertion results for exercise 1, including output equals input; one parameter and one buffer.

2. **Keep state stable across calls.** Call the same module on a second batch with the same width.
   **Expected:** same kernel object and parameter count 4.
   **Verify:** Save the assertion results for exercise 2, including same kernel object and parameter count 4.

3. **Check a known residual transform.** Assign an identity kernel and scale.5.
   **Expected:** output1.5*x.
   **Verify:** Save the assertion results for exercise 3, including output1.5*x.

4. **Reject incompatible feature width.** Pass a width3 row to the width2 module.
   **Expected:** ValueError naming feature width.
   **Verify:** Save the assertion results for exercise 4, including ValueError naming feature width.

5. **Validate a custom cube derivative.** Run grad check on Cube.apply at float64 values.2, -.7.
   **Expected:** grad check True.
   **Verify:** Save the assertion results for exercise 5, including grad check True.

6. **Inspect the incoming-gradient factor.** Differentiate the sum of 2*Cube(x) atx2.
   **Expected:** gradient24.
   **Verify:** Save the assertion results for exercise 6, including gradient24.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Custom module, Buffer, Grad check using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-025` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why is a buffer not just an ordinary tensor attribute?**

Buffers participate in state_dict and module device/dtype movement. An ordinary attribute can be omitted from those operations and cause inconsistent reconstruction.

**What does grad check not establish?**

It does not prove behavior on every branch, shape or nondifferentiable point. Add domain, boundary and composition tests alongside numerical derivative checks.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-026, Custom modules, residual paths, buffers and autograd checks.
Read courses/deep-learning-pytorch/guides/torch-026.md and courses/deep-learning-pytorch/lessons/torch-026.py. Direct prerequisites: `torch-025`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
