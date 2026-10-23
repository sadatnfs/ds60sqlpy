# torch-033: Inference mode, model contracts and bounded batching

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-032`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Inference is a bounded function with an input and output contract. The central investigation is concrete: Use float32 CPU rows1, 2 and3, 4. The finish condition is outputs0, 2 with shape(2, ). input unchanged. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Inference is a bounded function with an input and output contract. A model may accept many tensors that are syntactically legal but semantically wrong:missing batch axes, wrong feature order, unexpected dtype, nonfinite values oran oversized request. Validate these conditions before forward computation. Batching should preserve each record'sp re dict i on for a stateless model in the declared evaluation mode.

PyTorch inference_mode disables more autograd bookkeeping than no_grad and creates tensors with restrictions relevant to later gradient use. It is appropriate for a pure inference boundary, but should not be substituted blindly into training or gradient-based analysis. model.eval remains necessary for mode-dependent layers. This lesson uses a fixed linear model and no server, deployment or GPU so the contract can be tested locally.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-033](../../deep-learning-tensorflow/guides/tf-033.md) after deriving the shared numerical contract.

TensorFlow inference usually uses training=False and no gradienttape. PyTorch uses model.eval plus no_grad or inference_mode as separate controls. The paired contract checks use the same shape, finite-value and batch limits; framework mode flags do not replace input validation.

## Vocabulary and concepts

**Inference mode:** A PyTorch context disabling gradient recording and additional bookkeeping.

**Input contract:** The accepted shape, dtype, device, range and budget for prediction.

**Batch independence:** Agreement of a record predicted alone or with other records.

**Owned output:** Returned storage that cannot mutate caller or model state.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-033/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-033.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-033.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

The predict helper requires a CPU float32 tensor shaped(batch, 2), with batch size 1..4 and finite entries. It calls model.eval and uses inference_mode, then returns an owned clone suitable for caller inspection. The coefficient vector[2, -1] supplies an independent output oracle. Treat shape, dtype, device and value validation as different diagnostics rather than silently coercing every input.

## Worked example / walkthrough

### Example A: Predict a valid batch

The output has one scalar per record. The absence of gradient tracking is part of this inference-only contract.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
MODEL=nn.Linear(2,1,bias=False)
with torch.no_grad(): MODEL.weight.copy_(torch.tensor([[2.,-1.]]))
def predict(x):
    if not isinstance(x,torch.Tensor) or x.dtype!=torch.float32: raise TypeError('float32 tensor required')
    if x.device.type!='cpu': raise ValueError('CPU input required')
    if x.ndim!=2 or x.shape[1]!=2: raise ValueError('shape must be (batch,2)')
    if not 1<=len(x)<=4: raise ValueError('batch limit1..4')
    if not bool(torch.isfinite(x).all()): raise ValueError('finite input required')
    MODEL.eval()
    with torch.inference_mode(): output=MODEL(x).squeeze(-1)
    return output.clone()
x=torch.tensor([[1.,2.],[3.,4.]],dtype=torch.float32); result=predict(x)
assert result.tolist()==[0.,2.] and tuple(result.shape)==(2,) and not result.requires_grad
```

**Expected:** outputs0, 2 with shape(2, ).

### Example B: Check per-record batching parity

A training-mode BatchNorm layer could violate this property. The test therefore checks more than output shape.

```python
single=torch.cat([predict(x[i:i+1]) for i in range(len(x))])
torch.testing.assert_close(single,result,atol=0,rtol=0)
```

**Expected:** same values as batch prediction.

### Example C: Reject empty and oversized batches

Are source bound must be checked before computation. An empty batch also has no observations to score.

```python
for bad in [torch.empty((0,2)),torch.zeros((5,2))]:
    try: predict(bad)
    except ValueError as error: assert 'batch' in str(error)
    else: raise AssertionError('invalid batch accepted')
```

**Expected:** ValueError naming batch limit.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: outputs0, 2 with shape(2, ). input unchanged. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Predict a valid batch.** Use float32 CPU rows1, 2 and3, 4.
   **Expected:** outputs0, 2 with shape(2, ).
   **Verify:** Save the assertion results for exercise 1, including outputs0, 2 with shape(2, ).

2. **Check per-record batching parity.** Predict each row alone and concatenate.
   **Expected:** same values as batch prediction.
   **Verify:** Save the assertion results for exercise 2, including same values as batch prediction.

3. **Reject empty and oversized batches.** Pass shapes0 x2 and5 x2.
   **Expected:** ValueError naming batch limit.
   **Verify:** Save the assertion results for exercise 3, including ValueError naming batch limit.

4. **Reject shape and dtype ambiguity.** Pass a vector, a3-feature matrix and an int64 matrix.
   **Expected:** shape ValueErrors and dtype TypeError.
   **Verify:** Save the assertion results for exercise 4, including shape ValueErrors and dtype TypeError.

5. **Reject nonfinite values.** Pass aN aN feature and inspect the failure.
   **Expected:** ValueError for finite-value contract.
   **Verify:** Save the assertion results for exercise 5, including ValueError for finite-value contract.

6. **Preserve caller data.** Mutate the returned output and compare the original input.
   **Expected:** input unchanged.
   **Verify:** Save the assertion results for exercise 6, including input unchanged.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Inference mode, Input contract, Batch independence using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-032` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 inference mode](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad_mode.inference_mode.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Is inference_mode always better than no_grad?**

It removes additional bookkeeping but imposes restrictions on resulting tensors. Choose it for a pure inference boundary; use a differentiation-compatible context when later gradient work is intended.

**Why reject rather than silently cast an integer input?**

A strict API makes precision and meaning changes visible. If coercion is desired, it should be a declared and tested preprocessing policy.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-033, Inference mode, model contracts and bounded batching.
Read courses/deep-learning-pytorch/guides/torch-033.md and courses/deep-learning-pytorch/lessons/torch-033.py. Direct prerequisites: `torch-032`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
