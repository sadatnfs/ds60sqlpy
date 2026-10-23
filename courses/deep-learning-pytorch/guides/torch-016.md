# torch-016: Initialization, nonlinearities and gradient diagnostics

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-015`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Nonlinearity changes which functions a network can represent. The central investigation is concrete: Use inputs 00, 01, 10, 11 and two rectified differences. The finish condition is outputs 0, 1, 1, 0. both.6; the function is absolute difference. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Nonlinearity changes which functions a network can represent. Stacking linear layers without activations still produces one affine map. XOR assigns opposite labels to diagonally opposite corners of a square, so there is no linear threshold separating all four cases. Two rectified differences h1=max(x1-x2, 0), h2=max(x2-x1, 0) produce the exact binary pattern when added. This manual construction distinguishes representational capacity from whether an optimizer happens to find it.

Initialization selects a starting point and can preserve or break symmetry between units. Equal hidden weights can produce identical features and gradients, making units redundant. Gradient diagnostics should inspect where activations and derivatives become zero or nonfinite instead of assuming the architecture is incapable. PyTorch provides explicit initialization functions and no_grad assignment for controlled fixtures.

## Design decisions and when to use this method

Separate representational capacity from optimization. First show that the architecture can express a small required function using explicit parameters. Then investigate whether a chosen initialization and training procedure can find a useful solution. More epochs cannot make an affine-only map separate XOR in the original two input coordinates.

Choose an initialization in relation to the activation, feature scale and intended forward/backward variance behavior. Use controlled weights for a diagnostic, but do not mistake that manual construction for a successful training run. When testing layout translation, include a nonsymmetric fixture so an accidental transpose has an observable effect.

## Paired TensorFlow comparison

Compare [tf-016](../../deep-learning-tensorflow/guides/tf-016.md) after deriving the shared numerical contract.

The paired TensorFlow XOR construction uses the same ReLU math. Translate Keras Dense kernel orientation to PyTorch Linear weight orientation explicitly. Initialization APIs differ, but the capacity-versus-optimization distinction is framework independent.

## Vocabulary and concepts

**Nonlinearity:** A transformation that cannot be collapsed into one affine map.

**Initialization:** The policy choosing parameter values before training.

**Capacity:** The function family an architecture can represent.

**Symmetry:** Identical unit behavior preserved by identical state and updates.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-016/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-016.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-016.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use F.relu after a matrix product. In nn.Linear, the columns of a mathematical projection are the rows of the stored weight. torch.nn.init.zeros_ or constant_ set known initial state without constructing an optimization graph. Compare all four XOR inputs before training. A ReLU negative preactivation has zero local derivative; a zero gradient and a missing gradient path are not the same diagnosis.

## Prove the capacity boundary and then inspect optimization

Suppose a classifier uses an affine score \(s=a\) x1+b x2+c and predicts class 1 when \(s>0\). XOR requires(1, 0) and(0, 1) positive, so \(a+c>0\) and \(b+c>0\). It requires(0, 0) and(1, 1) nonpositive, so c≤0 and a+b+c≤0. Summing the positive requirements gives a+b+2c>0; summing the negative requirements gives the same quantity≤0. The contradiction proves that no such affine separator exists, independent of a random seed or training budget.

Stacking affine layers does not remove that boundary. `(XW1+b1)W2+b2 = X(W1W2)+(b1W2+b2)` is still affine in the input. A bottleneck can even restrict the possible rank. Nonlinear parameterization of the weights may change optimization behavior, but it does not create a nonlinear input function. Adding an engineered interaction feature would change the input representation and therefore the problem being considered.

The manual construction uses \(d=x_{1}-x_{2}\), h1=max(d, 0), h2=max(-d, 0), and \(\mathrm{output}=h_{1}+h_{2}\):

| Input | Raw difference pair | ReLU features | Output |
| --- | --- | --- | --- |
| (0, 0) | (0, 0) | (0, 0) | 0 |
| (0, 1) | (-1, 1) | (0, 1) | 1 |
| (1, 0) | (1, -1) | (1, 0) | 1 |
| (1, 1) | (0, 0) | (0, 0) | 0 |

Without ReLU, the two raw differences cancel everywhere. With ReLU, the sum is|x1-x2|. On binary corners that equals XOR, but on continuous inputs(.2, .8) and(.8, .2) it equals 0.6. That value is a function output, not automatically a calibrated probability or a new definition of a binary logical operator.

The XOR projection matrix[[1, -1], [-1, 1]] is symmetric. Consequently, W.T equalsW, so the original fixture alone cannot detect a forgotten transpose when copying a mathematical matrix into nn.Linear's stored(out, in) layout. The strengthened example adds a separate nonsymmetric matrix[[1, 2], [3, 4]]. For input[0, 1], XW gives[3, 4], while XW.T gives[2, 4]. That probe makes the storage translation observable while retaining the original XOR construction unchanged.

Activation gradients distinguish a dead region from a broken graph. ReLU at a negative preactivation has a connected derivative zero; at a positive one its derivative is one. At the kink, the framework uses its chosen convention. Repeatedly negative preactivations can therefore block useful gradient flow even though every operation is differentiable on the active path. Inspect activation signs and intermediate gradients before declaring the architecture incapable.

Identical hidden rows produce identical features on the same input. Equal gradients additionally require symmetric downstream influence and other state; unequal output weights can break that symmetry. If a whole ReLU network is initialized in a zero/symmetric configuration, both hidden activations and upstream signals can vanish, leaving ordinary gradient descent unable to create useful differences. Separate Parameter objects are not by themselves evidence of diverse features.

Variance-aware initialization gives a useful approximation. For independent zero-mean inputs and weights, a preactivation's variance scales roughly with \(\mathrm{fan}_{\mathrm{in}}\cdot \operatorname{Var}(\mathrm{weight})\cdot \operatorname{Var}(\mathrm{input})\). ReLU discards about half the second moment under a symmetric distribution, motivating an initialization scale near \(\frac{2}{\mathrm{fan}_{\mathrm{in}}}\) for that simplified setting. Those assumptions need not hold exactly for correlated finite data. Choose the documented initializer and gain for the intended activation rather than assuming every layer's default initialization implements that exact rule. [PyTorch 2.9 initialization APIs](https://docs.pytorch.org/docs/2.9/nn.init.html).

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

**Expected:** outputs 0, 1, 1, 0.

### Example B: Remove the nonlinearity

The two columns are opposites, so a linear sum cancels. Adding more linear layers would not create the piecewise behavior needed for XOR.

```python
assert (x@w).sum(1).tolist()==[0.,0.,0.,0.]
```

**Expected:** all four outputs 0.

### Example C: Map the construction into Linear

The XOR matrix is symmetric, so that fixture alone cannot detect a missing transpose. The separate asymmetric matrix makes the two orientations produce different outputs and checks the Linear storage convention independently.

```python
layer=nn.Linear(2,2,bias=False)
with torch.no_grad(): layer.weight.copy_(w.T)
torch.testing.assert_close(F.relu(layer(x)),h,atol=0,rtol=0)
asymmetric=torch.tensor([[1.,2.],[3.,4.]])
probe=nn.Linear(2,2,bias=False)
with torch.no_grad(): probe.weight.copy_(asymmetric.T)
torch.testing.assert_close(probe(x),x@asymmetric,atol=0,rtol=0)
assert not torch.equal(x@asymmetric,x@asymmetric.T)
```

**Expected:** module features equal manual features; the asymmetric probe distinguishes the two orientations.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: outputs 0, 1, 1, 0. both.6; the function is absolute difference. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Construct XOR by hand.** Use inputs 00, 01, 10, 11 and two rectified differences.
   **Expected:** outputs 0, 1, 1, 0.
   **Verify:** Save the assertion results for exercise 1, including outputs 0, 1, 1, 0.

2. **Remove the nonlinearity.** Sum the raw difference features without ReLU.
   **Expected:** all four outputs 0.
   **Verify:** Save the assertion results for exercise 2, including all four outputs 0.

3. **Map the construction into Linear.** Set a 2-to-2 bias-free Linear weight to W.T, then check a separate asymmetric matrix.
   **Expected:** module features equal manual features; the asymmetric probe distinguishes the two orientations.
   **Verify:** Save the assertion results for exercise 3, including module features equal manual features; the asymmetric probe distinguishes the two orientations.

4. **Inspect activation gradients.** Differentiate ReLU at-2 and 2.
   **Expected:** gradients 0 and 1.
   **Verify:** Save the assertion results for exercise 4, including gradients 0 and 1.

5. **Expose identical-unit symmetry.** Initialize both stored Linear rows identically and compare their outputs.
   **Expected:** two unit outputs match on every row.
   **Verify:** Save the assertion results for exercise 5, including two unit outputs match on every row.

6. **Transfer to continuous inputs.** Evaluate the fixed construction at(.2, .8) and(.8, .2).
   **Expected:** both.6; the function is absolute difference.
   **Verify:** Save the assertion results for exercise 6, including both.6; the function is absolute difference.

## Common pitfalls and diagnosis

If an affine-only model never solves XOR, derive the incompatible inequalities before increasing the training budget. If the manual nonlinear construction works but fitting fails, inspect initialization, active ReLU regions, gradient magnitudes and update policy. A connected zero gradient does not become nonzero by retain_grad or by detaching the value.

If a layout test passes with a square symmetric matrix, add a nonsymmetric probe before claiming transpose correctness. If identical units remain redundant, check both their initial rows and their downstream gradient signals rather than assuming all equal initial features must receive equal updates. If the construction returns 0.6 outside the binary corners, state the actual absolute-difference function instead of treating the value as an empirically validated XOR probability.

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



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-016, Initialization, nonlinearities and gradient diagnostics.
Read courses/deep-learning-pytorch/guides/torch-016.md and courses/deep-learning-pytorch/lessons/torch-016.py. Direct prerequisites: `torch-015`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
