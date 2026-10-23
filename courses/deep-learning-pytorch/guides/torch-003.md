# torch-003: Linear modules, parameters and matrix contracts

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-002`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A linear layer computes an affine transformation from input features to output features. The central investigation is concrete: UseX[[1, 2, 3], [0, 1, 0]], weight[[1, 0, -1]], bias2. The finish condition is outputs[[0], [2]], shape(2, 1). RuntimeError from incompatible matrix dimensions. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A linear layer computes an affine transformation from input features to output features. For a batch X shaped(B, I), PyTorch nn.Linear(I, O) stores weight shaped(O, I) and computes X@weight.T+bias. This storage orientation differs from the common mathematical W shaped(I, O) and from a Keras Dense kernel. The batch axis is not part of the parameter shape. Bias has one value per output feature and is shared across observations.

Annn.Parameter assigned to annn.Module is registered as trainable state. A plain tensor attribute is not automatically an optimizer parameter, even if it participates in arithmetic. Registration lets model.parameters(), state_dict and device/dtype conversion find the intended state. Shape inspection and a hand-calculated first row provide an independent check before any training occurs.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-003](../../deep-learning-tensorflow/guides/tf-003.md) after deriving the shared numerical contract.

Keras Dense stores a kernel shaped(input_features, output_features), while PyTorch nn.Linear stores(output_features, input_features). Copying values without transposing changes or breaks the computation. Both expose tracked trainable state, but PyTorch distinguishes Parameter registration from an ordinary tensor attribute.

## Vocabulary and concepts

**Affine map:** A matrix transformation plus an additive bias.

**Parameter registration:** Tracking model state for optimization and serialization.

**Weight layout:** The semantic orientation of stored input/output feature axes.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-003/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-003.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-003.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Construct nn.Linear(3, 1, bias=True, dtype=torch.float64). Assign known values under no_grad so initialization does not become part of an autograd graph. copy_ requires the stored layout(1, 3). Calling the module performs the forward computation; it does not update weights. parameters enumerates both weight and bias when enabled. Count scalar entries with numel, not the number of Parameter objects.

## Worked example / walkthrough

### Example A: Calculate a known affine layer

The first output is1-3+2=0, and the second is0+2=2. This calculation checks orientation and bias independently of random initialization.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

layer=nn.Linear(3,1,bias=True,dtype=torch.float64)
with torch.no_grad(): layer.weight.copy_(torch.tensor([[1.,0.,-1.]],dtype=torch.float64)); layer.bias.fill_(2.)
x=torch.tensor([[1.,2.,3.],[0.,1.,0.]],dtype=torch.float64); out=layer(x)
torch.testing.assert_close(out,torch.tensor([[0.],[2.]],dtype=torch.float64),atol=1e-12,rtol=0)
```

**Expected:** outputs[[0], [2]], shape(2, 1).

### Example B: Inspect registered state

There are two Parameter objects but four trainable scalar values. Parameter count and tensor count answer different questions.

```python
assert sum(p.numel() for p in layer.parameters())==4
assert set(layer.state_dict())=={'weight','bias'}
```

**Expected:** 4 scalars; keys weight, bias.

### Example C: Compare with a mathematical matrix

The transpose is a layout translation, not a change in the modeled function. A non symmetric rectangular fixture makes an accidental orientation error visible.

```python
mathematical_w=layer.weight.T
assert tuple(mathematical_w.shape)==(3,1)
torch.testing.assert_close(x@mathematical_w+layer.bias,out,atol=1e-12,rtol=0)
```

**Expected:** direct result equals module output.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: outputs[[0], [2]], shape(2, 1). RuntimeError from incompatible matrix dimensions. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate a known affine layer.** UseX[[1, 2, 3], [0, 1, 0]], weight[[1, 0, -1]], bias2.
   **Expected:** outputs[[0], [2]], shape(2, 1).
   **Verify:** Save the assertion results for exercise 1, including outputs[[0], [2]], shape(2, 1).

2. **Inspect registered state.** Count weight and bias scalar entries and inspect state_dict keys.
   **Expected:** 4 scalars; keys weight, bias.
   **Verify:** Save the assertion results for exercise 2, including 4 scalars; keys weight, bias.

3. **Compare with a mathematical matrix.** Transpose the stored weight and calculate X@W+b directly.
   **Expected:** direct result equals module output.
   **Verify:** Save the assertion results for exercise 3, including direct result equals module output.

4. **Remove the intercept explicitly.** Create a bias-free layer with the same stored weights.
   **Expected:** 3 parameters; outputs-2 and0.
   **Verify:** Save the assertion results for exercise 4, including 3 parameters; outputs-2 and0.

5. **Expose an unregistered tensor.** Compare a Module holding a plain requires_grad tensor with one holding Parameter.
   **Expected:** plain module has0 registered parameters; proper module has1.
   **Verify:** Save the assertion results for exercise 5, including plain module has0 registered parameters; proper module has1.

6. **Reject wrong feature width.** Pass a2-feature row to the3-input layer.
   **Expected:** RuntimeError from incompatible matrix dimensions.
   **Verify:** Save the assertion results for exercise 6, including RuntimeError from incompatible matrix dimensions.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Affine map, Parameter registration, Weight layout using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-002` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why does Linear store a transposed-looking weight?**

Its public contract defines weight as(out, in) and applies the transpose during the batched row-vector computation. The important check is the documented layout, not which notation fee l s more natural.

**Can a tensor have gradients but be absent from an optimizer?**

Yes. Autograd tracking and module registration are separate. A plain requires_grad tensor can receive gradients while model.parameters omits it.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-003, Linear modules, parameters and matrix contracts.
Read courses/deep-learning-pytorch/guides/torch-003.md and courses/deep-learning-pytorch/lessons/torch-003.py. Direct prerequisites: `torch-002`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
