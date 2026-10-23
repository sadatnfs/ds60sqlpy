# torch-002: Tensors, devices, dtypes, strides and views

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-001`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A PyTorch tensor has values plus metadata: shape, dtype, device, strides and gradient-tracking state. The central investigation is concrete: Create a2x3 float64 CPU tensor from values 0..5. The finish condition is shape(2, 3), stride(3, 1), CPU, float64. RuntimeError for incompatible trailing dimensions. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A PyTorch tensor has values plus metadata: shape, dtype, device, strides and gradient-tracking state. Shape tells you the number of elements along each axis; strides describe how an index moves through storage. A view can share storage with another tensor, so mutation through one reference may change the other. clone creates independent storage. Transpose changes the interpretation of axes and often produces a noncontiguous view. reshape may return a view or a copy, so code should not infer ownership solely from its name.

Device and dtype are part of a computation contract. This course uses CPU explicitly, with float64 for hand-derived numerical checks and float32 for small neural modules unless stated otherwise. Broadcasting aligns trailing dimensions and can silently create pairwise results. A vector of shape(3, ) subtracted from a column(3, 1) produces(3, 3), not three paired residuals.

## Design decisions and when to use this method

Use a view when shared storage is intentional and the consumer's mutation behavior is controlled. Use clone when the interface promises independent storage. Use contiguous to satisfy a layout requirement only after establishing that requirement; it can return the existing tensor when the layout is already suitable, so it is not an ownership guarantee.

Choose dtype and device at the input boundary rather than hoping an operation converts them as intended. Floating model inputs, integer class indices and Boolean masks have different roles. Before a paired loss or subtraction, require the semantic axes and record identities to match, not merely equal lengths or a broadcast-compatible shape.

## Paired TensorFlow comparison

Compare [tf-002](../../deep-learning-tensorflow/guides/tf-002.md) after deriving the shared numerical contract.

TensorFlow tensors expose shape, dtype and device too, but ordinary TensorFlow tensors are immutable values, while PyTorch tensors commonly allow in-place mutation and shared-storage views. NumPy-like stride reasoning is therefore central to PyTorch ownership. Both frameworks can silently broadcast a vector against a column into pairwise residuals.

## Vocabulary and concepts

**Stride:** Storage offset in elements for advancing one position along an axis.

**View:** A tensor sharing underlying storage with another tensor.

**Device:** The execution and storage location such as CPU.

**Broadcasting:** Expansion of compatible trailing dimensions during an operation.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-002/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-002.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-002.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

torch.arange creates a one-dimensional tensor; reshape supplies the desired axes. stride returns element offsets rather than byte offsets. Transpose .T swaps matrix axes. view requires a compatible storage layout, while contiguous can materialize a suitable layout. clone is the explicit ownership operation. Use shape equality before paired subtraction and keep device placement visible with device='cpu'.

## Trace axes, storage and pairing separately

For a contiguous 2-by-3 tensor containing 0 through 5, the stride tuple(3, 1) means one step along the first axis moves three stored elements and one step along the second moves one. Ignoring a nonzero base storage offset, element(i, j) is located at element offset 3 i+j. In float64 each element uses eight bytes, so offset 5 corresponds to 40 bytes from that base. Strides describe storage movement in elements, not a count of rows or bytes.

Transposing gives shape(3, 2) and strides(1, 3). The value at transposed[2, 1] is the original[1, 2], still five. No rearrangement of the underlying values is required for that interpretation. A contiguous materialization may allocate a new ordering for a later operation, but the fact that a tensor is contiguous does not establish that nobody else shares its storage. The official view documentation makes that aliasing boundary explicit. [PyTorch 2.9 tensor views](https://docs.pytorch.org/docs/2.9/tensor_view.html).

The worked sequence deliberately mutates state. Example A creates x, Example B takes its first-row view and changes x[0, 0] to 99, and Example C clones the now-mutated tensor. Its correct comparison is therefore clone=-1 versus original=99. Re-running Example C alone with an unrelated x would be a different fixture. Keep the stated sequential scratch-file contract visible when reproducing the examples.

Copying storage and changing the gradient graph are different operations. clone provides independent storage but can remain connected to the source through autograd. Detach changes the differentiation boundary but can still share storage. A later inference snapshot that needs both properties may require both operations. Do not infer either property from a convenient display or from reshape, which can choose a view or a copy according to layout.

Broadcasting provides a second independent counterexample. With v=[1, 2, 3] and column=v[:, None], the right-aligned shapes are(1, 3) and(3, 1). Their difference is:

| Column value | Difference against vector 1, 2, 3 |
| --- | --- |
| 1 | [0, 1, 2] |
| 2 | [-1, 0, 1] |
| 3 | [-2, -1, 0] |

The intended paired differences are only the diagonal zeros. The broadcast operation instead creates nine comparisons whose squared mean is \(\frac{12}{9}=\frac{4}{3}\). Reducing that grid to one scalar cannot restore the lost pairing. A model can therefore optimize a nonzero objective even though every intended prediction equals its target.

A practical tensor boundary should name every axis, required dtype, device and ownership rule. A shape check catches a column/vector mismatch, but it cannot detect that two equally shaped batches have different record orders or units. Keep those semantic checks beside the tensor metadata. The framework enforces legal arithmetic; the application defines which arithmetic corresponds to the task.

## Worked example / walkthrough

### Example A: Inspect shape and stride

The last axis advances by one stored element and the first by three. These metadata explain the matrix layout without relying on a printed table alone.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

x=torch.arange(6,dtype=torch.float64,device='cpu').reshape(2,3)
assert tuple(x.shape)==(2,3) and x.stride()==(3,1) and x.device.type=='cpu' and x.dtype==torch.float64
```

**Expected:** shape(2, 3), stride(3, 1), CPU, float64.

### Example B: Expose shared storage

Basic slicing returns a view here. A function receiving that view can mutate caller-owned data unless it copies or documents the ownership contract.

```python
row=x[0]; row[0]=99
assert x[0,0].item()==99
```

**Expected:** original x[0, 0] becomes 99.

### Example C: Create an independent copy

clone copies storage and preserves a differentiable relationship when gradients are enabled. Detaching and copying are separate operations discussed later.

```python
owned=x.clone(); owned[0,0]=-1
assert owned[0,0].item()==-1 and x[0,0].item()==99
```

**Expected:** clone starts-1; original remains 99.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: shape(2, 3), stride(3, 1), CPU, float64. RuntimeError for incompatible trailing dimensions. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect shape and stride.** Create a2x3 float64 CPU tensor from values 0..5.
   **Expected:** shape(2, 3), stride(3, 1), CPU, float64.
   **Verify:** Save the assertion results for exercise 1, including shape(2, 3), stride(3, 1), CPU, float64.

2. **Expose shared storage.** Slice the first row, change its first value, and inspect the original tensor.
   **Expected:** original x[0, 0] becomes 99.
   **Verify:** Save the assertion results for exercise 2, including original x[0, 0] becomes 99.

3. **Create an independent copy.** Clone the tensor, change the clone and compare the original.
   **Expected:** clone starts-1; original remains 99.
   **Verify:** Save the assertion results for exercise 3, including clone starts-1; original remains 99.

4. **Trace a transposed layout.** Transpose x and inspect shape, strides and contiguity.
   **Expected:** shape(3, 2), stride(1, 3), noncontiguous.
   **Verify:** Save the assertion results for exercise 4, including shape(3, 2), stride(1, 3), noncontiguous.

5. **Detect a pairing broadcast.** Subtract vector[1, 2, 3] from its column representation and inspect the result.
   **Expected:** shape(3, 3), while equal-vector subtraction has shape(3, ).
   **Verify:** Save the assertion results for exercise 5, including shape(3, 3), while equal-vector subtraction has shape(3, ).

6. **Reject incompatible arithmetic.** Add tensors shaped(2, 3) and(4, ) and capture the shape failure.
   **Expected:** RuntimeError for incompatible trailing dimensions.
   **Verify:** Save the assertion results for exercise 6, including RuntimeError for incompatible trailing dimensions.

## Common pitfalls and diagnosis

When a loss unexpectedly becomes a matrix, print full shape tuples before flattening or squeezing. A vector and a one-column matrix can have the same length while producing a pairwise grid. Check the actual row identities before any reshape repair.

When caller data changes, identify views and in-place writes. Replacing view with reshape does not establish independent ownership; test the promised mutation boundary with a deliberately changed output. When view rejects a layout, inspect strides and the required logical order instead of transposing until dimensions happen to fit. A contiguous copy can solve a layout requirement while leaving a semantic axis mistake untouched. When arithmetic raises a device or dtype error, repair the declared boundary explicitly rather than broadly converting class indices, masks and model features to the same representation.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Stride, View, Device using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-001` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does reshape always copy?**

No. It returns a view when the layout permits and may copy otherwise. Use clone when independent storage is the contract and inspect layout when performance matters.

**Why can a shape bug produce no exception?**

Broadcasting may define a valid larger operation. The framework checks arithmetic compatibility, not whether the new axes match the intended prediction unit.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-002, Tensors, devices, dtypes, strides and views.
Read courses/deep-learning-pytorch/guides/torch-002.md and courses/deep-learning-pytorch/lessons/torch-002.py. Direct prerequisites: `torch-001`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
