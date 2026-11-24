# torch-033: Inference mode, model contracts and bounded batching

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-032`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Implement an inference function with an explicit input contract that rejects ambiguous inputs and never mutates caller data.

Central investigation: Predict float32 rows [1, 2] and [3, 4], compare per-record and batched calls, then pass empty, oversized, wrongly typed and nonfinite inputs.

Finish condition: The batch predicts 0 and 2 with shape (2,), single-row calls agree, invalid shapes raise ValueError, an int64 matrix raises TypeError, a NaN raises ValueError, and the caller's input is unchanged.

The worked examples demonstrate the mechanism; exercises 1-3 transfer it to new inputs and exercises 4-6 extend it to failures and boundary cases. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Inference is a bounded function with an input and output contract. A model may accept many tensors that are syntactically legal but semantically wrong: missing batch axes, wrong feature order, unexpected dtype, nonfinite values or an oversized request. Validate these conditions before forward computation. Batching should preserve each record's prediction for a stateless model in the declared evaluation mode.

PyTorch inference_mode disables more autograd bookkeeping than no_grad and creates tensors with restrictions relevant to later gradient use. It is appropriate for a pure inference boundary, but should not be substituted blindly into training or gradient-based analysis. model.eval remains necessary for mode-dependent layers. This lesson uses a fixed linear model and no server, deployment or GPU so the contract can be tested locally.

## Design decisions and when to use this method

Choose a pure inference boundary when callers need predictions rather than derivatives. Validate the declared dtype, device, rank, feature meaning and request budget before forward computation. Keep a separate path for gradient-based explanation or adaptation rather than silently disabling its graph.

Use a dedicated evaluation model with an explicit output ownership contract. Decide whether batch independence is required for the application and test it under that model's actual mode. Finite inputs alone do not guarantee finite outputs for arbitrary magnitudes, so a production contract also needs a justified range or output-finiteness policy beyond this tiny fixture.

## Paired TensorFlow comparison

Compare [tf-033](../../deep-learning-tensorflow/guides/tf-033.md) after deriving the shared numerical contract.

TensorFlow inference usually uses training=False and no gradienttape. PyTorch uses model.eval plus no_grad or inference_mode as separate controls. The paired contract checks use the same shape, finite-value and batch limits; framework mode flags do not replace input validation.

## Vocabulary and concepts

**Inference mode:** A PyTorch context disabling gradient recording and additional bookkeeping.

**Input contract:** The accepted shape, dtype, device, range and budget for prediction.

**Batch independence:** Agreement of a record predicted alone or with other records.

**Owned output:** Returned storage that cannot mutate caller or model state.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-033`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-033.py` under `.learning/expansion/torch-033/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

The predict helper requires a CPU float32 tensor shaped (batch, 2), with batch size 1..4 and finite entries. It calls model.eval and uses inference_mode, then returns an owned clone suitable for caller inspection. The coefficient vector [2, -1] supplies an independent output oracle. Treat shape, dtype, device and value validation as different diagnostics rather than silently coercing every input.

## Trace validation, mode, storage and batching as separate boundaries

The function accepts a CPU float32 tensor shaped (B, 2), with \(1\le B\le 4\) and finite entries. Those checks occur before the model call. They are not interchangeable: an integer matrix has the wrong representation policy, a one-dimensional vector lacks the required batch axis, a three-feature matrix has the wrong schema, and a five-row matrix exceeds the declared work bound. A predictable validation order helps callers diagnose the first rejected condition.

The model computes 2 x_0-x_1. For [1, 2] and [3, 4], the results are zero and two. Linear returns (B, 1), and squeeze(-1) removes only the known singleton output-feature axis to produce (B). A blanket squeeze() would also remove the batch axis when \(B=1\), creating a scalar result and breaking a stable one-result-per-record interface. This is why axis-specific shape operations belong in the API contract.

model.eval() changes mode-dependent behavior such as ordinary Dropout and BatchNorm. It does not disable autograd. no_grad disables ordinary reverse-mode recording for operations in its scope. inference_mode removes additional bookkeeping, including some view/version tracking, and also has restrictions relevant to later differentiation. The choice should follow the consumer's intended use, not a rule that one context is always faster or universally better. [PyTorch 2.9 inference_mode](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad_mode.inference_mode.html).

The worked function leaves inference_mode before cloning the result. That clone gives the caller independent normal tensor storage with requires_grad false under this path. It does not reconnect a gradient to the original model computation. The output can be inspected and mutated without changing caller input or model state. Cloning inside the inference context would still create an inference tensor, so the location of the operation matters if later ordinary tensor behavior is part of the interface.

For this stateless affine model, each row's output depends only on that row and fixed weights. Predicting one row alone or alongside the other must therefore agree. A training-mode BatchNorm layer could depend on neighboring records, and some models intentionally contain cross-record operations. A model configured without running BatchNorm statistics can also retain batch-dependent behavior in evaluation. Batch independence is a tested property of this predictor, not a universal theorem about eval().

Record identity remains necessary even when numeric parity holds. Concatenating singleton predictions in a different order can create a correctly shaped but misaligned result. A future batching service must preserve request-to-row mapping, not merely return the correct multiset of values. The local helper starts no server and proves no authentication, queueing, cancellation or concurrent-serving behavior.

The model object is dedicated to this teaching inference path. Calling eval on a model simultaneously shared with a training loop would mutate shared mode state. An output clone cannot repair that ownership problem. A real integration should define separate model instances or a deliberate synchronization/immutability policy, then test state preservation. The fixture does not claim thread-safe serving from a global mutable model.

Finite-value validation is also narrower than an output guarantee. A very large finite float32 input multiplied by two can overflow even though isfinite(input) passed. The literal rows here are small and produce exact finite outputs. If a service promises finite predictions for all accepted requests, it must bound feature magnitudes appropriately or validate output finiteness and define a failure policy. Silently clipping inputs would change the represented model unless that preprocessing rule was declared and tested.

Likewise, shape validation cannot identify swapped features or changed units. The [2, -1] coefficient vector assumes one fixed ordering. A valid two-column float32 array carrying different semantics can pass every tensor check and still be the wrong request. Save names, units and preprocessing metadata with the predictor, and use known input/output cases through that complete path.

The paired TensorFlow helper accepts a float32 NumPy array and returns a copied NumPy output. Its immutable tensor operations and explicit copy have different mechanics from PyTorch inference tensors, but the application-level goals are comparable: strict input policy, one output per record, batch parity and no caller-data mutation. Compare those observed contracts rather than treating training=False and inference_mode as identical APIs.

## Worked example / walkthrough

### Example A: Predict a valid batch

The output has one scalar per record. The absence of gradient tracking is part of this inference-only contract.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

MODEL = nn.Linear(2, 1, bias=False)
with torch.no_grad():
    MODEL.weight.copy_(torch.tensor([[2.0, -1.0]]))


def predict(x):
    if not isinstance(x, torch.Tensor) or x.dtype != torch.float32:
        raise TypeError("float32 tensor required")
    if x.device.type != "cpu":
        raise ValueError("CPU input required")
    if x.ndim != 2 or x.shape[1] != 2:
        raise ValueError("shape must be (batch,2)")
    if not 1 <= len(x) <= 4:
        raise ValueError("batch limit1..4")
    if not bool(torch.isfinite(x).all()):
        raise ValueError("finite input required")
    MODEL.eval()
    with torch.inference_mode():
        output = MODEL(x).squeeze(-1)
    return output.clone()


x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float32)
result = predict(x)
assert result.tolist() == [0.0, 2.0] and tuple(result.shape) == (2,) and not result.requires_grad
```

**Expected:** outputs 0, 2 with shape (2, ).

### Example B: Check per-record batching parity

A training-mode BatchNorm layer could violate this property. The test therefore checks more than output shape.

```python
single = torch.cat([predict(x[i : i + 1]) for i in range(len(x))])
torch.testing.assert_close(single, result, atol=0, rtol=0)
```

**Expected:** same values as batch prediction.

### Example C: Reject empty and oversized batches

A resource bound must be checked before computation. An empty batch also has no observations to score.

```python
for bad in [torch.empty((0, 2)), torch.zeros((5, 2))]:
    try:
        predict(bad)
    except ValueError as error:
        assert "batch" in str(error)
    else:
        raise AssertionError("invalid batch accepted")
```

**Expected:** ValueError naming batch limit.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Predict a valid batch. Predict exercise 6, Preserve caller data, from its prompt alone: Mutate the returned output and compare the original input. Then explain why this finish condition holds: The batch predicts 0 and 2 with shape (2,), single-row calls agree, invalid shapes raise ValueError, an int64 matrix raises TypeError, a NaN raises ValueError, and the caller's input is unchanged. Keep each prediction beside the observed value.

## Exercises

1. **Predict a new valid batch.** Predict the float32 rows [0, 1], [2, 0] and [1, 1] with the lesson's weight [2, -1].
   **Expected:** outputs [-1, 4, 1] with shape (3,).
   **Verify:** In a fresh process, the exercise checks confirm `predict(rows).tolist() == [-1.0, 4.0, 1.0]`.

2. **Check the batch boundary.** Predict a batch of four rows of ones, then a batch of five.
   **Expected:** four rows return shape (4,); five rows raise ValueError.
   **Verify:** In a fresh process, the exercise checks confirm `tuple(predict(torch.ones((4, 2))).shape) == (4,)` and `predict(torch.ones((5, 2)))` raises `ValueError`.

3. **Reject a float64 batch.** Pass the three valid rows converted to float64.
   **Expected:** TypeError rather than a silent conversion.
   **Verify:** In a fresh process, the exercise checks confirm `predict(rows.double())` raises `TypeError`.

4. **Reject shape and dtype ambiguity.** Pass a vector, a 3-feature matrix and an int64 matrix.
   **Expected:** shape ValueErrors and dtype TypeError.
   **Verify:** In a fresh process, the exercise checks confirm for every looped case, `predict(bad)` raises `kind`.

5. **Reject nonfinite values.** Pass a NaN feature and inspect the failure.
   **Expected:** ValueError for finite-value contract.
   **Verify:** In a fresh process, the exercise checks confirm `predict(torch.tensor([[float('nan'), 1.0]]))` raises `ValueError` and the raised error satisfies `'finite' in str(error)`.

6. **Preserve caller data.** Mutate the returned output and compare the original input.
   **Expected:** input unchanged.
   **Verify:** In a fresh process, the exercise checks confirm `torch.equal(x, saved)`.

## Common pitfalls and diagnosis

If a singleton call returns a scalar, inspect squeeze dimensions before changing caller code. If batch and singleton predictions differ, check mode, normalization and any cross-record computation. If outputs mutate source data, inspect aliases and where the owned copy is created. If a later gradient operation fails on an inference tensor, decide whether the original context was appropriate instead of forcing requires_grad onto a disconnected result.

If a finite request produces a nonfinite prediction, inspect arithmetic range and the declared output policy; input finiteness alone was insufficient. If all tensor checks pass but predictions are semantically wrong, check feature order and units. Keep these local contract failures separate from untested service-level concerns such as concurrent model mutation or request scheduling.

## Progressive hints

Hint 1: Example B (Check per-record batching parity) alters one assumption of Example A (Predict a valid batch). Hint 2: exercise 4, Reject shape and dtype ambiguity, should end at shape ValueErrors and dtype TypeError. Work backward from it. Hint 3: exercise 5, Reject nonfinite values, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Reject empty and oversized batches, from its inputs alone. Predict whether exercise 3, Reject a float64 batch, survives one changed input. Then explain Inference mode, Input contract, Batch independence in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Predict a valid batch) cannot be rebuilt without help, revisit `torch-032` first. Otherwise keep your exercise 2 attempt, Check the batch boundary, as a regression case alongside a fresh transfer input, then continue along the course plan.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 inference mode](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad_mode.inference_mode.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Is inference_mode always better than no_grad?**

It removes additional bookkeeping but imposes restrictions on resulting tensors. Choose it for a pure inference boundary; use a differentiation-compatible context when later gradient work is intended.

**Why reject rather than silently cast an integer input?**

A strict API makes precision and meaning changes visible. If coercion is desired, it should be a declared and tested preprocessing policy.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-033, Inference mode, model contracts and bounded batching.
Read courses/deep-learning-pytorch/guides/torch-033.md and courses/deep-learning-pytorch/lessons/torch-033.py. Direct prerequisites: `torch-032`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
