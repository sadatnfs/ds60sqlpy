# torch-026: Custom modules, residual paths, buffers and autograd checks

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-025`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Write a custom module and a custom autograd Function whose state, shape checks and backward rule are verified explicitly.

Central investigation: Build a width-2 residual module with a scale buffer, apply known kernels and validate a custom cube derivative with gradcheck.

Finish condition: The zero-kernel residual returns its input with one parameter and one buffer, the identity kernel with scale 0.5 returns 1.5x, a width-3 input raises ValueError, gradcheck passes for Cube, and the incoming factor 2 gives gradient 24 at x = 2.

The worked examples demonstrate the mechanism; exercises 1-3 transfer it to new inputs and exercises 4-6 extend it to failures and boundary cases. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Custom modules should make state ownership and differentiation explicit. Parameters are optimized; buffers are tracked but normally fixed; temporary activations are rebuilt during forward. A residual branch adds a transformed input to the original, so feature dimensions must match or an explicit projection must reconcile them. Creating new parameters in forward would change model identity and invalidate optimizer membership.

A custom differentiable function should be checked against independent derivatives before being trusted in a large network. PyTorch gradcheck uses finite differences, usually with float64 inputs, to compare a backward formula with the numerical behavior of forward. Passing a few checks is useful evidence under those inputs, not a proof for every branch or nondifferentiable point. This lesson combines a simple residual module with a tiny custom cube function so both registration and derivative contracts remain inspectable.

## Design decisions and when to use this method

Use a custom module to express a reusable computation with a stable state inventory. Create persistent learned state once and validate the feature contract on later calls. Choose a residual connection when its identity path is part of the intended architecture, not simply because addition makes a shape mismatch disappear.

Prefer ordinary differentiable PyTorch operations when they express the computation correctly. Write autograd.Function only when a concrete operation requires a custom rule, and then specify its input domain, upstream-gradient behavior and supported derivative orders. Numerical checks complement analytic and composition tests; they do not certify every branch automatically.

## Paired TensorFlow comparison

Compare [tf-026](../../deep-learning-tensorflow/guides/tf-026.md) after deriving the shared numerical contract.

Keras custom layers often create weights in build and define call; PyTorch modules usually register state in __init__ and define forward. TensorFlow custom-gradient mechanisms and PyTorch autograd.Function both require a correct local derivative multiplied by the incoming gradient.

## Vocabulary and concepts

**Custom module:** A reusable computation with explicitly registered state.

**Buffer:** Tracked tensor state outside the optimizer parameter set.

**Grad check:** A numerical comparison of a backward rule with finite differences.

**Incoming gradient:** The derivative from later operations supplied to a local backward rule.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-026`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-026.py` under `.learning/expansion/torch-026/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Assign nn.Parameter in __init__, register a scale buffer, and implement forward without allocating new trainable state. Use named_parameters and named_buffers to inspect ownership. A torch.autograd.Function defines static forward and backward methods; save_for_backward stores inputs needed later. gradcheck perturbs double-precision inputs and should avoid kinks. The cube derivative is \(3\cdot {x}^{2}\) times the incoming gradient.

## Derive residual gradients and stable module identity

For X shaped (B, D), a square kernel K shaped (D, D) and scalar scale s, the module computes \(Y=X+sXK\). Both terms have shape (B, D). A different branch width requires an explicit projection or a different architecture. Broadcasting an unrelated tensor into the residual sum may be legal arithmetic but would not satisfy this feature contract.

At \(K=0\) and \(s=1\), the forward map is exactly Y=X. That does not make the branch untrainable. For upstream \(G=\frac{\partial L}{\partial Y}\), the matrix derivatives are \(\frac{\partial L}{\partial X}=G+sGK^{\mathsf T}\) and \(\frac{\partial L}{\partial K}=sX^{\mathsf T}G\). With the fixture X=[[1, 2], [3, 4]] and L equal to the sum of output entries, G is all ones, so dL/dK=[[4, 4], [6, 6]] even at \(K=0\). The input derivative is G because the zero branch adds no additional input sensitivity. The skip path preserves a direct derivative route while the branch can begin learning.

Example C changes K to identity and s to 0.5. Its forward result is 1.5X. Under the same hypothetical summed loss, dL/dX=1.5G and dL/dK=[[2, 2], [3, 3]]. The paired TensorFlow residual has no scale buffer and therefore gives 2 X when its kernel is identity. That difference is an intentional mathematical configuration difference, not a framework disagreement. Match the scale before comparing corresponding derivatives.

The module owns one Parameter object with four scalar entries and one scalar buffer. Counting objects and counting scalars answer different questions. Parameters participate in named_parameters and are candidates for optimizer membership. The registered scale buffer participates in module state and device/dtype movement but is not automatically passed to an optimizer. Its current construction does not request gradients. An ordinary tensor attribute would not automatically receive all of those registration behaviors.

state_dict is not the complete program. It contains the registered kernel and persistent buffer, but reconstruction still needs the module class and width argument. Python configuration such as width is not made into serialized tensor state merely because it is an attribute. A release must preserve that construction contract alongside the tensors. Also, a state_dict mapping is not by itself an independent snapshot of every underlying tensor; clone the values when comparing against later in-place mutations.

Stable object identity matters as much as a stable parameter count. Replacing a four-element Parameter with a fresh four-element Parameter inside forward keeps the scalar count unchanged while leaving an existing optimizer holding the old object. Gradients can then appear on the new parameter without an update from that optimizer. The unchanged exercise checks both identity and count to expose this failure. Keras build/add_weight and PyTorch __init__/Parameter use different construction idioms, but both need a persistent tracked object across calls.

## Treat a custom backward as a local vector-Jacobian product

For \(f(x)=x^3\), the local derivative is 3 \({x}^{2}\). backward receives the derivative from later computation, so it must return \(\mathrm{grad\_output}\times3x^2\). At \(x=2\), the derivative of `2 * f(x)` is \(2\cdot 12=24\). Returning only 3 \({x}^{2}\) would pass a unit-upstream test but fail this composition. For a vector of independently cubed elements, the returned gradient has the same shape and multiplies each incoming component by its own local derivative.

save_for_backward preserves the tensor values required by the rule and lets autograd enforce relevant lifetime/version checks. Do not mutate saved input storage between forward and backward or detach a value that must support a higher-order derivative. A function with several inputs returns a corresponding derivative entry for each differentiable input, and None where that input has no requested derivative under the declared contract. [Extending PyTorch 2.9 autograd](https://docs.pytorch.org/docs/2.9/notes/extending.html).

gradcheck perturbs real-valued inputs and compares numerical sensitivities with the backward rule. The supplied float64 points 0.2 and -0.7 avoid a nondifferentiable branch, and the analytic derivatives are 0.12 and 1.47. Finite precision, probe size and conditioning still matter. A forward implementation that changes branches at the probe point may not have the derivative the numerical test assumes. Overlapping storage can also invalidate an interpretation that perturbations affect one independent coordinate.

A first-derivative check does not establish double backward, forward-mode support, arbitrary broadcasting or performance. Add the relevant contract tests when those features are actually required. The fixture's cube is small enough to inspect symbolically, and the upstream-factor test catches a distinct error from the basic numerical comparison. None of these checks requires a compiled extension or an external package.

## Worked example / walkthrough

### Example A: Build an identity residual

A zero branch makes the initial residual an exact identity. The branch can still receive gradients because its input is nonzero.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


class Residual(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.width = width
        self.kernel = nn.Parameter(torch.zeros((width, width), dtype=torch.float64))
        self.register_buffer("scale", torch.tensor(1.0, dtype=torch.float64))

    def forward(self, x):
        if x.ndim != 2 or x.shape[1] != self.width:
            raise ValueError("feature width mismatch")
        return x + self.scale * (x @ self.kernel)


class Cube(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return x**3

    @staticmethod
    def backward(ctx, grad_output):
        (x,) = ctx.saved_tensors
        return grad_output * 3 * x * x


module = Residual(2)
x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float64)
assert torch.equal(module(x), x)
assert set(dict(module.named_parameters())) == {"kernel"} and set(dict(module.named_buffers())) == {
    "scale"
}
```

**Expected:** output equals input; one parameter and one buffer.

### Example B: Keep state stable across calls

Batch length changes transient activations, not the number of learned coefficients. Stable state is necessary for optimizer and checkpoint consistency.

```python
identity = id(module.kernel)
module(torch.ones((1, 2), dtype=torch.float64))
assert id(module.kernel) == identity and sum(p.numel() for p in module.parameters()) == 4
```

**Expected:** same kernel object and parameter count 4.

### Example C: Check a known residual transform

The buffer changes forward behavior while remaining outside the trainable parameter list. It therefore belongs in the serialized state contract.

```python
with torch.no_grad():
    module.kernel.copy_(torch.eye(2, dtype=torch.float64))
    module.scale.fill_(0.5)
torch.testing.assert_close(module(x), 1.5 * x, atol=1e-12, rtol=0)
```

**Expected:** output \(1.5\cdot x\).

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Build an identity residual. Predict exercise 6, Inspect the incoming-gradient factor, from its prompt alone: Differentiate the sum of 2*Cube(x) at x = 2. Then explain why this finish condition holds: The zero-kernel residual returns its input with one parameter and one buffer, the identity kernel with scale 0.5 returns 1.5x, a width-3 input raises ValueError, gradcheck passes for Cube, and the incoming factor 2 gives gradient 24 at x = 2. Keep each prediction beside the observed value.

## Exercises

1. **Apply a swapping kernel.** Create Residual(2), set its kernel to [[0, 1], [1, 0]] and its scale buffer to 2, and evaluate the row [1, 2].
   **Expected:** output [[5, 4]].
   **Verify:** In a fresh process, the exercise checks confirm `swap(xs).tolist() == [[5.0, 4.0]]`.

2. **Predict state for a wider module.** Create Residual(3) and count its parameter scalars and buffers.
   **Expected:** 9 kernel scalars and 1 buffer.
   **Verify:** In a fresh process, the exercise checks confirm `sum((p.numel() for p in wide_residual.parameters())) == 9` and `len(list(wide_residual.buffers())) == 1`.

3. **Differentiate Cube at a new point.** Backpropagate the sum of 3*Cube(x) at x = -1.
   **Expected:** gradient 9.
   **Verify:** In a fresh process, the exercise checks confirm `point.grad.item() == 9`.

4. **Reject incompatible feature width.** Pass a width 3 row to the width 2 module.
   **Expected:** ValueError naming feature width.
   **Verify:** In a fresh process, the exercise checks confirm `module(torch.ones((1, 3), dtype=torch.float64))` raises `ValueError`.

5. **Validate a custom cube derivative.** Run gradcheck on Cube.apply at float64 values 0.2, -0.7.
   **Expected:** gradcheck returns True.
   **Verify:** In a fresh process, the exercise checks confirm `torch.autograd.gradcheck(Cube.apply, (probe,), eps=1e-06, atol=1e-05, rtol=0.001)`.

6. **Inspect the incoming-gradient factor.** Differentiate the sum of 2*Cube(x) at x = 2.
   **Expected:** gradient 24.
   **Verify:** In a fresh process, the exercise checks confirm `value.grad.item() == 24`.

## Common pitfalls and diagnosis

If an identity residual receives no kernel gradient, inspect the branch input and graph before concluding that a zero forward branch cannot learn. If the parameter count stays fixed but training stops, compare object identities in the module and optimizer. If loading tensors produces a different function, check constructor width and buffer values as well as weights.

If a custom backward passes only when the outer coefficient is one, multiply the output by a different upstream factor and inspect the vector-Jacobian product. If gradcheck fails near a kink or at float32 precision, choose a justified smooth float64 probe before loosening tolerances. If higher derivatives are required, test them explicitly rather than inferring them from a first-order pass. Preserve saved-tensor ownership instead of bypassing autograd checks with untracked mutation.

## Progressive hints

Hint 1: Example B (Keep state stable across calls) alters one assumption of Example A (Build an identity residual). Hint 2: exercise 4, Reject incompatible feature width, should end at ValueError naming feature width. Work backward from it. Hint 3: exercise 5, Validate a custom cube derivative, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Check a known residual transform, from its inputs alone. Predict whether exercise 3, Differentiate Cube at a new point, survives one changed input. Then explain Custom module, Buffer, Grad check in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Build an identity residual) cannot be rebuilt without help, revisit `torch-025` first. Otherwise keep your exercise 2 attempt, Predict state for a wider module, as a regression case alongside a fresh transfer input, then continue along the course plan.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 autograd](https://docs.pytorch.org/docs/2.9/autograd.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Why is a buffer not just an ordinary tensor attribute?**

Buffers participate in state_dict and module device/dtype movement. An ordinary attribute can be omitted from those operations and cause inconsistent reconstruction.

**What does gradcheck not establish?**

It does not prove behavior on every branch, shape or nondifferentiable point. Add domain, boundary and composition tests alongside numerical derivative checks.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-026, Custom modules, residual paths, buffers and autograd checks.
Read courses/deep-learning-pytorch/guides/torch-026.md and courses/deep-learning-pytorch/lessons/torch-026.py. Direct prerequisites: `torch-025`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
