# cuda-098: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Derive the input VJP

Multiply upstream by a and the positive mask.

**Approach.** Derive the input vector-Jacobian product for `y = max(0, a*x + b)`: the gradient of x is `upstream * a * mask`, where `mask` is 1 where the preactivation is positive and 0 otherwise.

**Why it is correct here.** The chain rule multiplies the upstream gradient by the derivative of the ReLU, the mask, and by the derivative of the affine part, `a`. At `x = 2` with `a = 2`, `b = 1`, the preactivation is 5 and the derivative is 2.

**A plausible wrong approach.** Using the output `y` instead of a mask, `upstream * a * y`, scales gradients by activation values and is wrong for every positive input not equal to 1.

**How to verify.** Compare the custom backward with autograd of the reference expression on random inputs away from the kink.

## Exercise 2: Derive bias gradient

Sum masked upstream values.

**Approach.** Derive the bias gradient as the sum of masked upstream values: with upstream `[1, 3]` and mask `[0, 1]`, it is `1*0 + 3*1 = 3`.

**Why it is correct here.** The bias is shared across all elements, so its gradient accumulates over them. Only positions with positive preactivation pass gradient through the ReLU.

**A plausible wrong approach.** Returning the upstream sum without masking gives 4, including a contribution from a position where the ReLU blocked gradient.

**How to verify.** The reference asserts `bias_grad == 3`. Compare against autograd for a tensor with mixed signs.

## Exercise 3: Run finite differences away from a kink

Use symmetric perturbations and a suitable epsilon.

**Approach.** Run central finite differences away from the kink: at `x = 2` with `eps = 1e-5`, `(f(x+eps) - f(x-eps)) / (2*eps)` is about 2.

**Why it is correct here.** Both perturbations stay in the linear region, so the central difference equals the derivative up to rounding. The reference asserts agreement within `1e-8` in float64.

**A plausible wrong approach.** Running the check in float32 with a tiny epsilon loses precision to cancellation and fails even when the analytic gradient is right.

**How to verify.** Use float64 inputs, as `torch.autograd.gradcheck` expects, and check a few points on both sides of the kink.

## Exercise 4: Explain a failed kink gradcheck

The derivative is not unique at the boundary.

**Approach.** Explain a gradcheck failure at `x = -0.5`, where the preactivation is 0: the central difference straddles the kink and gives `(2*eps - 0)/(2*eps) = 1`, while PyTorch's ReLU chooses subgradient 0 there.

**Why it is correct here.** The derivative is not unique at the kink, so any value between 0 and the right derivative is a valid subgradient choice. Finite differences pick an average.

**A plausible wrong approach.** Changing the backward to return 1 at the kink so the check passes chooses a convention for the test's sake.

**How to verify.** Test the kink separately with the documented subgradient, and run gradcheck only at points away from it.

## Exercise 5: Specify higher-order support

Do not imply it from first-order success.

**Approach.** Specify higher-order support explicitly: if the backward is not itself differentiable, mark the operator as first-order only, for example with `once_differentiable`.

**Why it is correct here.** A correct first derivative says nothing about whether the backward function supports differentiation again, which methods like gradient penalties require.

**A plausible wrong approach.** Assuming double backward works because first-order gradcheck passed leads to silent zero second derivatives.

**How to verify.** Run `gradgradcheck` if second order is supported, or confirm a clear error is raised.

## Exercise 6: Compare each framework reference

Compare native forward and backward independently.

**Approach.** Compare each framework's native reference separately: PyTorch autograd of the reference expression and TensorFlow's `GradientTape` of the same expression, each for forward and backward.

**Why it is correct here.** Each framework binding may differ in subgradient conventions or dtype handling. Separate comparisons localize a mismatch.

**A plausible wrong approach.** Comparing PyTorch's custom op with TensorFlow's custom op only checks they agree with each other.

**How to verify.** Use the same inputs and upstream values in both frameworks and compare forward and backward results within tolerance.

## Reference observation

Finite-difference derivative approximately 2 and bias VJP 3.

The reference file is `courses/cuda/python/references/cuda-098_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
