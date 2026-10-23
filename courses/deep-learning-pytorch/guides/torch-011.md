# torch-011: nn.Module, registered parameters and explicit training loops

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-010`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Annn. The central investigation is concrete: Build Scalar Model with weight 0 and buffer offset 0. The finish condition is one parameter weight; one buffer offset; both in state_dict. same weight object and one parameter. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Annn.Module owns a model's registered parameters, buffers and child modules. Its forward method defines a computation, but the optimizer membership and training loop remain explicit. A plain tensor attribute is not automatically a Parameter. A buffer is tracked state that moves with the module and appears in state_dict without being optimized by default. This distinction is useful for fixed preprocessing statistics, running counts or nontrainable masks.

Calling model(x) routes through Module machinery and forward; it does not calculate a loss or apply an update. A complete loop selects parameters for an optimizer, clears gradients, computes an objective, backpropagates and steps. Replacing a Parameter after constructing an optimizer does not automatically update the optimizer object list. This lesson uses a scalar module to make ownership and membership observable before larger architectures hide them.

## Design decisions and when to use this method

Put persistent learned state and child layers in the module construction path, then use forward to compute from that state. Register fixed tensor state as a buffer when it should follow module conversions and persistence. Keep ordinary metadata as ordinary attributes only when its lifecycle does not require those tensor-state mechanisms.

Finish deliberate model construction and device/dtype placement before creating an optimizer. If a later algorithm replaces or adds parameters, update optimizer membership and any retained optimizer state explicitly. A module's current parameter iterator is not a live subscription that automatically rewrites an already constructed optimizer.

## Paired TensorFlow comparison

Compare [tf-011](../../deep-learning-tensorflow/guides/tf-011.md) after deriving the shared numerical contract.

Keras layers often create weights in build when input shape becomes known; PyTorch modules commonly create Parameter and child layers in__init__. PyTorch leaves the standard loop explicit rather than requiring compile/fit. Both frameworks distinguish tracked state from arbitrary attributes, but their registration idioms differ.

## Vocabulary and concepts

**Module:** An object organizing computation and tracked model state.

**Buffer:** Tracked non parameter tensor state.

**Optimizer membership:** The parameter objects explicitly owned by an optimizer.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-011/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-011.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-011.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Define parameters in__init__ after super().__init__, using nn.Parameter or registered child layers. register_buffer names a nontrainable tensor. forward uses those attributes without creating a new parameter on every call. named_parameters and named_buffers expose different state sets. state_dict includes both. An SGD optimizer captures references to the parameter objects supplied at construction.

## Trace module-owned state and optimizer-owned references

The scalar model owns a Parameter named weight and a buffer named offset. Both are scalar float64 tensors, but only weight is selected by model.parameters(). Its forward expression is weight*x+offset. The offset influences predictions while remaining fixed under the demonstrated SGD step because it is not in that optimizer's parameter list.

| Item | Registered category | In parameters() | In default state_dict() | Changed by this SGD step |
| --- | --- | --- | --- | --- |
| weight | Parameter | Yes | Yes | Yes |
| offset | Persistent buffer | No | Yes | No |
| An arbitrary plain tensor attribute | Ordinary attribute | No | No | Only if separately managed |

These are registration defaults, not a law that buffers can never participate in autograd or that every registered Parameter must be trainable. requires_grad and optimizer membership remain separate choices. A buffer registered with persistent=False still follows module conversion but is omitted from state_dict. The supplied offset uses the default persistent behavior. [PyTorch 2.9 Module state APIs](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Module.html).

A call to model(x) routes through Module machinery and its forward method. At weight=offset=0, the three inputs 1, 2, 3 produce three zeros. No loss, backward call or optimizer step is implied by that invocation. The explicit loop then clears gradients, computes the paired mean squared objective, backpropagates and applies SGD. The one-step weight \(\frac{28}{15}\) is the same scalar oracle as the earlier chapter, while offset remains zero.

Converting the module to float32 moves both registered tensors through the module conversion mechanism. A plain auxiliary tensor could remain at its old dtype or device and later cause an operation mismatch. This example checks CPU dtype movement; it does not qualify a GPU placement path. In a larger model, also inspect optimizer state after a late conversion because momentum or other optimizer tensors have their own lifecycle.

Object identity makes the stale-optimizer failure concrete. At construction, the optimizer stores a reference to the original weight object. Replacing fresh.weight with a new Parameter changes what forward reads, but the old optimizer list still refers to the former object. A new backward can populate the replacement's grad while step examines the old object's gradient instead. Rebuilding or deliberately editing parameter groups is therefore part of the model-change operation, not an optional cleanup detail.

Creating Parameters inside forward causes a related failure. Repeated calls can create new objects after the optimizer captured its membership, so the current computation and the objects being updated diverge. A stable model should preserve its intended parameter identities across batch sizes unless it implements a deliberate, tested dynamic-state policy. The final exercise compares calls of length one and four for that reason.

State serialization also has a boundary. state_dict supplies a mapping of registered parameter and persistent-buffer state, but it is not automatically an immutable historical snapshot of independent storage. If a diagnostic must survive later in-place model mutation, clone the relevant values or serialize them at a defined point. Later checkpoint lessons distinguish a saved model state from optimizer, RNG and data-order state needed for a training restart.

For the paired Keras model, compare the represented function before comparing the training interface. A no-bias Dense kernel and the zero-offset scalar PyTorch model can represent the same map, but their storage layouts and construction APIs differ. Explicitly match dtype, denominator and update budget; a high-level training call can report a pre-update loss just as a retained PyTorch loss tensor can.

## Worked example / walkthrough

### Example A: Inspect module state

The buffer is serialized and follows device/dtype conversions, but it is not an optimizer parameter. A plain attribute would not provide the same tracking contract.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
class ScalarModel(nn.Module):
    def __init__(self):
        super().__init__(); self.weight=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); self.register_buffer('offset',torch.tensor(0.,dtype=torch.float64))
    def forward(self,x): return self.weight*x+self.offset
model=ScalarModel()
assert set(dict(model.named_parameters()))=={'weight'} and set(dict(model.named_buffers()))=={'offset'}
assert set(model.state_dict())=={'weight','offset'}
```

**Expected:** one parameter weight; one buffer offset; both in state_dict.

### Example B: Check a forward call

A forward call only computes the current function. Neither parameter registration nor calling the module performs training.

```python
x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x
assert torch.equal(model(x),torch.zeros_like(x)) and model.weight.item()==0
```

**Expected:** three zero outputs; weight unchanged.

### Example C: Run one explicit loop step

The optimizer consumes only the registered Parameter. The buffer influences forward but remains fixed under this update.

```python
optimizer=torch.optim.SGD(model.parameters(),lr=.1); optimizer.zero_grad(set_to_none=True)
loss=((model(x)-y)**2).mean(); loss.backward(); optimizer.step()
np.testing.assert_allclose(model.weight.item(),28/15,atol=1e-12,rtol=0); assert model.offset.item()==0
```

**Expected:** weight \(\frac{28}{15}\); buffer still 0.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: one parameter weight; one buffer offset; both in state_dict. same weight object and one parameter. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect module state.** Build Scalar Model with weight 0 and buffer offset 0.
   **Expected:** one parameter weight; one buffer offset; both in state_dict.
   **Verify:** Save the assertion results for exercise 1, including one parameter weight; one buffer offset; both in state_dict.

2. **Check a forward call.** Runx 1, 2, 3 through the zero-weight module.
   **Expected:** three zero outputs; weight unchanged.
   **Verify:** Save the assertion results for exercise 2, including three zero outputs; weight unchanged.

3. **Run one explicit loop step.** Use SGD.1 and mean squared error, clearing gradients before backward.
   **Expected:** weight \(\frac{28}{15}\); buffer still 0.
   **Verify:** Save the assertion results for exercise 3, including weight \(\frac{28}{15}\); buffer still 0.

4. **Move dtype through registered state.** Convert the module to float32 and inspect parameter and buffer dtypes.
   **Expected:** both float32.
   **Verify:** Save the assertion results for exercise 4, including both float32.

5. **Expose stale optimizer membership.** Create an optimizer, replace the module Parameter, and inspect captured object identity.
   **Expected:** optimizer still holds old Parameter, not replacement.
   **Verify:** Save the assertion results for exercise 5, including optimizer still holds old Parameter, not replacement.

6. **Keep parameter count stable across calls.** Call a fresh module on batches of length 1 and 4 and compare parameter identities.
   **Expected:** same weight object and one parameter.
   **Verify:** Save the assertion results for exercise 6, including same weight object and one parameter.

## Common pitfalls and diagnosis

If a tensor is missing from state_dict or model.parameters(), inspect how it was assigned and registered. If a fixed statistic stays on another dtype or device, check whether it is an unregistered attribute rather than a buffer. If a new parameter has a gradient but never moves, compare object identities against every optimizer parameter group.

If parameter count changes after a forward call, look for construction inside forward or an untracked container of child modules. If a state snapshot changes later, inspect shared storage instead of assuming a dictionary copy made tensor copies. If a framework comparison disagrees after one update, reconstruct the scalar \(\frac{28}{15}\) oracle and verify whether an extra trainable bias or different reduction was introduced.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Module, Buffer, Optimizer membership using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-010` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why not create a Parameter in forward?**

Repeated calls could create new state after the optimizer has captured its parameter list. That breaks stable model identity and training membership.

**What belongs in a buffer?**

Tensor state that should move and serialize with the model but is not optimized as a Parameter, such as a fixed normalization statistic or running state.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-011, nn.Module, registered parameters and explicit training loops.
Read courses/deep-learning-pytorch/guides/torch-011.md and courses/deep-learning-pytorch/lessons/torch-011.py. Direct prerequisites: `torch-010`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
