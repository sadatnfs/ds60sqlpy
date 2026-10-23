# torch-016: Initialization, nonlinearities and gradient diagnostics

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-015`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Nonlinearity changes which functions a network can represent. The central investigation is concrete: Use inputs00, 01, 10, 11 and two rectified differences. The finish condition is outputs0, 1, 1, 0. both.6; the function is absolute difference. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Nonlinearity changes which functions a network can represent. Stacking linear layers without activations still produces one affine map. XOR assigns opposite labels to diagonal l y opposite corners of a square, so there is no linear threshold separating all four cases. Two rectified differences h1=max(x1-x2, 0), h2=max(x2-x1, 0) produce the exact binary pattern when added. This manual construction distinguishes representation al capacity from whether an optimizer happens to find it.

Initialization selects a starting point and can preserve or break symmetry between units. Equal hidden weights can produce identical features and gradients, making units redundant. Gradient diagnostics should inspect where activations and derivatives become zero or nonfinite instead of assuming the architecture is in capable. PyTorch provides explicit initialization functions and no_grad assignment for controlled fixtures.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-016](../../deep-learning-tensorflow/guides/tf-016.md) after deriving the shared numerical contract.

The paired TensorFlow XOR construction uses the same ReLU math. Translate Keras Dense kernel orientation to PyTorch Linear weight orientation explicitly. Initialization APIs differ, but the capacity-versus-optimization distinction is framework independent.

## Vocabulary and concepts

**Nonlinearity:** A transformation that cannot be collapsed into one affine map.

**Initialization:** The policy choosing parameter values before training.

**Capacity:** The function family an architecture can represent.

**Symmetry:** Identical unit behavior preserved by identical state and updates.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-016/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-016.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-016.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

UseF.relu after a matrix product. Innn.Linear, the columns of a mathematical projection are the rows of the stored weight. torch.nn.init.zeros_ or constant_ set known initial state without constructing an optimization graph. Compare all four XOR inputs before training. A ReLU negative preactivation has zero local derivative; a zero gradient and a missing gradient path are not the same diagnosis.

## Worked example / walkthrough

### Example A: Construct XOR by hand

Each hidden unit detects one direction of difference. ReLU prevents positive and negative contributions from cancelling.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

x=torch.tensor([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
w=torch.tensor([[1.,-1.],[-1.,1.]])
h=F.relu(x@w); output=h.sum(1)
assert output.tolist()==[0.,1.,1.,0.]
```

**Expected:** outputs0, 1, 1, 0.

### Example B: Remove the nonlinearity

The two columns are opposite s, so a linear sum cancels. Adding more linear layers would not create the piecewise behavior needed for XOR.

```python
assert (x@w).sum(1).tolist()==[0.,0.,0.,0.]
```

**Expected:** all four outputs0.

### Example C: Map the construction into Linear

The explicit transpose checks PyTorch's stored layout. A correct mathematical matrix with the wrong assignment orientation can change a function silently when shapes are square.

```python
layer=nn.Linear(2,2,bias=False)
with torch.no_grad(): layer.weight.copy_(w.T)
torch.testing.assert_close(F.relu(layer(x)),h,atol=0,rtol=0)
```

**Expected:** module features equal manual features.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: outputs0, 1, 1, 0. both.6; the function is absolute difference. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Construct XOR by hand.** Use inputs00, 01, 10, 11 and two rectified differences.
   **Expected:** outputs0, 1, 1, 0.
   **Verify:** Save the assertion results for exercise 1, including outputs0, 1, 1, 0.

2. **Remove the nonlinearity.** Sum the raw difference features without ReLU.
   **Expected:** all four outputs0.
   **Verify:** Save the assertion results for exercise 2, including all four outputs0.

3. **Map the construction into Linear.** Seta2-to-2 bias-free Linear weight to W.T and apply ReLU.
   **Expected:** module features equal manual features.
   **Verify:** Save the assertion results for exercise 3, including module features equal manual features.

4. **Inspect activation gradients.** Differentiate ReLU at-2 and2.
   **Expected:** gradients0 and1.
   **Verify:** Save the assertion results for exercise 4, including gradients0 and1.

5. **Expose identical-unit symmetry.** Initialize both stored Linear rows identically and compare their outputs.
   **Expected:** two unit outputs match on every row.
   **Verify:** Save the assertion results for exercise 5, including two unit outputs match on every row.

6. **Transfer to continuous inputs.** Evaluate the fixed construction at(.2, .8) and(.8, .2).
   **Expected:** both.6; the function is absolute difference.
   **Verify:** Save the assertion results for exercise 6, including both.6; the function is absolute difference.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Nonlinearity, Initialization, Capacity using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-015` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does adding depth always increase nonlinear capacity?**

Not if all layers are affine and no other nonlinearity intervenes. Their composition remains affine.

**Why test a manual solution before fitting?**

It proves the architecture can represent the fixture and separates an optimization failure from a capacity limitation.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-016, Initialization, nonlinearities and gradient diagnostics.
Read courses/deep-learning-pytorch/guides/torch-016.md and courses/deep-learning-pytorch/lessons/torch-016.py. Direct prerequisites: `torch-015`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
