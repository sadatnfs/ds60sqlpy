# torch-003: Linear modules, parameters and matrix contracts

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-002`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A linear layer computes an affine transformation from input features to output features. The central investigation is concrete: UseX[[1, 2, 3], [0, 1, 0]], weight[[1, 0, -1]], bias 2. The finish condition is outputs[[0], [2]], shape(2, 1). RuntimeError from incompatible matrix dimensions. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A linear layer computes an affine transformation from input features to output features. For a batch X shaped(B, I), PyTorch nn.Linear(I, O) stores weight shaped(O, I) and computes X@weight.T+bias. This storage orientation differs from the common mathematical W shaped(I, O) and from a Keras Dense kernel. The batch axis is not part of the parameter shape. Bias has one value per output feature and is shared across observations.

An nn.Parameter assigned to an nn.Module is registered as trainable state. A plain tensor attribute is not automatically an optimizer parameter, even if it participates in arithmetic. Registration lets model.parameters(), state_dict and device/dtype conversion find the intended state. Shape inspection and a hand-calculated first row provide an independent check before any training occurs.

## Design decisions and when to use this method

Use an affine layer as a directly inspectable baseline when an additive combination of declared features is meaningful. Add nonlinear layers only when the task and evidence justify their extra behavior. The same shape can encode different feature orders or units, so an accepted matrix multiplication is not a complete model-schema check.

Keep parameter registration separate from trainability and optimizer membership. A registered Parameter can be frozen, and an optimizer can still hold an obsolete parameter object after a module is replaced. This early chapter establishes the state inventory; later transfer and checkpoint chapters examine how that inventory changes over time.

## Paired TensorFlow comparison

Compare [tf-003](../../deep-learning-tensorflow/guides/tf-003.md) after deriving the shared numerical contract.

Keras Dense stores a kernel shaped(input_features, output_features), while PyTorch nn.Linear stores(output_features, input_features). Copying values without transposing changes or breaks the computation. Both expose tracked trainable state, but PyTorch distinguishes Parameter registration from an ordinary tensor attribute.

## Vocabulary and concepts

**Affine map:** A matrix transformation plus an additive bias.

**Parameter registration:** Tracking model state for optimization and serialization.

**Weight layout:** The semantic orientation of stored input/output feature axes.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-003`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-003.py` under `.learning/expansion/torch-003/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Construct nn.Linear(3, 1, bias=True, dtype=torch.float64). Assign known values under no_grad so initialization does not become part of an autograd graph. copy_ requires the stored layout(1, 3). Calling the module performs the forward computation; it does not update weights. parameters enumerates both weight and bias when enabled. Count scalar entries with numel, not the number of Parameter objects.

## Derive the forward map and parameter contracts

Let a batch have B observations, I input features and O outputs. The mathematical row-vector expression uses X shaped(B, I), W shaped(I, O) and b shaped(O), producing Y shaped(B, O). PyTorch stores the corresponding Linear weight as(O, I), so its forward expression is X@weight.T+b. The transpose translates the storage convention; it is not a proposal to exchange the observation and feature axes. [PyTorch 2.9 Linear](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Linear.html).

| Object | This fixture | General contract |
| --- | --- | --- |
| Input X | (2, 3) | (B, I) |
| Stored weight | (1, 3) | (O, I) |
| Mathematical W | (3, 1) | (I, O) |
| Bias | (1, ) | (O, ) |
| Output | (2, 1) | (B, O) |

For the first row[1, 2, 3], the products are 1, 0, -3. Adding bias 2 gives zero. The second row[0, 1, 0] contributes zero before the same shared bias, giving two. The bias is not a separate fitted offset for each observation. WithO outputs there areI×O weight scalars and O bias scalars, orO(I+1) total. ChangingB changes the number of evaluated rows, not the parameter count.

Suppose an upstream loss supplies derivatives g1 and g2 for these two scalar outputs. The stored weight gradient is[g1, 2g1+g2, 3g1], and the bias gradient isg 1+g2. The bias gradient sums over the batch because one bias participates in both outputs. Each input-row gradient is its upstream scalar multiplied by[1, 0, -1]. These shapes can be predicted before using autograd: weight.grad must match(1, 3), bias.grad must match(1, ), and input derivatives match(2, 3).

A feature-order mistake can remain invisible to every dimension check. If the first input is accidentally exported as[3, 2, 1], its output becomes \(3-1+2=4\) instead of zero while all shapes remain valid. Likewise, a centimeter-to-meter conversion requires a corresponding weight interpretation if the represented function is to stay the same. The data schema must therefore preserve names, order and units beside the width.

Autograd and module registration answer different questions. A plain tensor with requires_grad=True can participate in a differentiable computation, but model.parameters() will not discover it merely because it is an attribute. Assigning nn.Parameter registers it. Registration does not require that gradients currently be enabled: freezing can turn requires_grad off while retaining the parameter in the module's state. Buffers form another category of registered state introduced later.

The known-value initialization runs under no_grad so assignment is not recorded as part of the differentiation graph. It does not make the layer permanently nontrainable. Calling the layer computes outputs but does not update parameters; an optimizer update is a separate later operation. These distinctions let the reader locate whether a failure concerns the forward function, the differentiation graph, the state inventory or the update mechanism.

## Worked example / walkthrough

### Example A: Calculate a known affine layer

The first output is \(1-3+2=0\), and the second is \(0+2=2\). This calculation checks orientation and bias independently of random initialization.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

layer = nn.Linear(3, 1, bias=True, dtype=torch.float64)
with torch.no_grad():
    layer.weight.copy_(torch.tensor([[1.0, 0.0, -1.0]], dtype=torch.float64))
    layer.bias.fill_(2.0)
x = torch.tensor([[1.0, 2.0, 3.0], [0.0, 1.0, 0.0]], dtype=torch.float64)
out = layer(x)
torch.testing.assert_close(
    out, torch.tensor([[0.0], [2.0]], dtype=torch.float64), atol=1e-12, rtol=0
)
```

**Expected:** outputs[[0], [2]], shape(2, 1).

### Example B: Inspect registered state

There are two Parameter objects but four trainable scalar values. Parameter count and tensor count answer different questions.

```python
assert sum(p.numel() for p in layer.parameters()) == 4
assert set(layer.state_dict()) == {"weight", "bias"}
```

**Expected:** 4 scalars; keys weight, bias.

### Example C: Compare with a mathematical matrix

The transpose is a layout translation, not a change in the modeled function. A non symmetric rectangular fixture makes an accidental orientation error visible.

```python
mathematical_w = layer.weight.T
assert tuple(mathematical_w.shape) == (3, 1)
torch.testing.assert_close(x @ mathematical_w + layer.bias, out, atol=1e-12, rtol=0)
```

**Expected:** direct result equals module output.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: outputs[[0], [2]], shape(2, 1). RuntimeError from incompatible matrix dimensions. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate a known affine layer.** UseX[[1, 2, 3], [0, 1, 0]], weight[[1, 0, -1]], bias 2.
   **Expected:** outputs[[0], [2]], shape(2, 1).
   **Verify:** Save the assertion results for exercise 1, including outputs[[0], [2]], shape(2, 1).

2. **Inspect registered state.** Count weight and bias scalar entries and inspect state_dict keys.
   **Expected:** 4 scalars; keys weight, bias.
   **Verify:** Save the assertion results for exercise 2, including 4 scalars; keys weight, bias.

3. **Compare with a mathematical matrix.** Transpose the stored weight and calculate X@W+b directly.
   **Expected:** direct result equals module output.
   **Verify:** Save the assertion results for exercise 3, including direct result equals module output.

4. **Remove the intercept explicitly.** Create a bias-free layer with the same stored weights.
   **Expected:** 3 parameters; outputs-2 and 0.
   **Verify:** Save the assertion results for exercise 4, including 3 parameters; outputs-2 and 0.

5. **Expose an unregistered tensor.** Compare a Module holding a plain requires_grad tensor with one holding Parameter.
   **Expected:** plain module has 0 registered parameters; proper module has 1.
   **Verify:** Save the assertion results for exercise 5, including plain module has 0 registered parameters; proper module has 1.

6. **Reject wrong feature width.** Pass a2-feature row to the 3-input layer.
   **Expected:** RuntimeError from incompatible matrix dimensions.
   **Verify:** Save the assertion results for exercise 6, including RuntimeError from incompatible matrix dimensions.

## Common pitfalls and diagnosis

If a matrix product fails, nameB, I and O and check the shared feature dimension before adding a transpose. If output width unexpectedly grows, inspect the bias axis. If dimensions pass but a prediction differs, calculate the first row's dot product and then inspect feature order and units.

If a tensor receives a gradient but does not move, compare its identity with the objects returned by model.parameters() and held by the optimizer. Conversely, a frozen Parameter can remain in state_dict without receiving a gradient. Count scalar entries with numel; counting Parameter objects would report two objects instead of four scalars in this fixture. During framework comparison, transpose the Dense kernel into the Linear storage layout explicitly and compare the first forward result before interpreting any training difference.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Affine map, Parameter registration, Weight layout using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-002` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Why does Linear store a transposed-looking weight?**

Its public contract defines weight as(out, in) and applies the transpose during the batched row-vector computation. The important check is the documented layout, not which notation feels more natural.

**Can a tensor have gradients but be absent from an optimizer?**

Yes. Autograd tracking and module registration are separate. A plain requires_grad tensor can receive gradients while model.parameters omits it.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-003, Linear modules, parameters and matrix contracts.
Read courses/deep-learning-pytorch/guides/torch-003.md and courses/deep-learning-pytorch/lessons/torch-003.py. Direct prerequisites: `torch-002`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
