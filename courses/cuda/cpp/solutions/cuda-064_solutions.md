# cuda-064: explanatory solutions

## Mechanism review

A custom ML operator has a forward contract and, when differentiable, a backward contract. State supported shape, strides, dtype, device, aliasing and stream behavior. Reject unsupported inputs before unsafe access. The operator must integrate with the framework's ownership and current-stream rules, not merely return plausible numbers. Compare against a readable framework reference and the framework's optimized or compiled path where available. Measure full training or inference scope, including backward, transfers and launch overhead. A faster forward kernel can still make training slower or produce wrong gradients.

## Exercise 1

For affine \(y=ax+b\) with a=3, b=1 and x=\([-1,0,2]\), forward output is \([-2,1,7]\). If a scalar loss sums outputs, each input gradient is three. A custom forward that returns the right values but backward returns one is mathematically wrong despite passing the forward fixture.

**Approach:** Compute forward 3x + 1 on [-1, 0, 2], then check gradients of the summed loss with central finite differences.

**Why it is correct:** Forward gives [-2, 1, 7], and each input gradient of sum(3x + 1) is the slope 3.

**A plausible wrong approach:** A backward pass returning 1 passes every forward test while giving wrong gradients to training.

**How to verify:** The reference asserts forward == [-2.0, 1.0, 7.0] and every finite-difference gradient within 1e-8 of 3.

## Exercise 2

For a fused bias-plus-ReLU, derivative at a nonzero preactivation is one when positive and zero when negative, multiplied by incoming gradient. The exact zero point needs the framework's chosen convention. A finite-difference check near a kink can be misleading, so test smooth points and the explicit boundary policy separately.

**Approach:** Multiply the incoming gradient by 1 for positive preactivations and 0 for negative ones.

**Why it is correct:** ReLU's derivative is a step, so the mask selects which gradients pass.

**A plausible wrong approach:** Finite-differencing exactly at zero straddles the kink and gives one half.

**How to verify:** Test points away from zero numerically, and check the zero convention against the framework.

## Exercise 3

Every component is three. Also test parameter gradients if a and b are learnable in the declared interface.

**Approach:** Differentiate sum(3x + 1) with respect to each x.

**Why it is correct:** Each derivative is 3, independent of x.

**A plausible wrong approach:** Returning the forward values as gradients confuses outputs with derivatives.

**How to verify:** Compare analytic gradients with the finite differences in the reference.

## Exercise 4

Either implement stride-aware indexing, make an explicit accounted copy or reject unsupported layouts; do not reinterpret shape as contiguity.

**Approach:** Use stride-aware indexing, make an explicit copy, or reject non-contiguous inputs.

**Why it is correct:** A transposed view has the same shape but different strides.

**A plausible wrong approach:** Indexing as contiguous reads elements in the wrong order.

**How to verify:** Pass a transposed tensor and compare against the reference.

## Exercise 5

Raise a clear validation error before launch or select a documented fallback; never cast silently if it changes the operator contract.

**Approach:** Raise a validation error before launch or use a documented fallback.

**Why it is correct:** The operator contract defines supported dtypes.

**A plausible wrong approach:** Silently casting can change precision and results.

**How to verify:** Pass an unsupported dtype and assert the error.

## Exercise 6

Forward/reference parity, backward checks, boundary and invalid-input tests, stream/lifetime correctness, real GPU evidence when claimed and end-to-end comparison against a strong framework baseline.

**Approach:** Require forward parity, gradient checks, edge and invalid tests, stream safety, GPU evidence and baseline comparison.

**Why it is correct:** Together these show the operator is correct and worthwhile.

**A plausible wrong approach:** Accepting it on speed alone ignores correctness and maintenance.

**How to verify:** Run each check and record results before adoption.

## Self-check answers

1. **What are the input gradients for loss = sum(3x+1)?** 3 for every element.
2. **A kernel assumes contiguous tensors but accepts transposed views. What is wrong?** It reads with the wrong strides; it must check strides and reject or convert noncontiguous input.
3. **What should an unsupported dtype do?** Raise a clear error before any device access.

## Numerical reference and its limits

The [CPU reference](../references/cuda-064_cpu.py) reproduces worked example 1 and prints `{'forward': [-2.0, 1.0, 7.0], 'CPU_finite_difference_gradients': [3.000000000019653, 2.9999999999752442, 3.000000000064062]}`.

## Transfer review

Forward/reference parity, backward checks, boundary and invalid-input tests, stream/lifetime correctness, real GPU evidence when claimed and end-to-end comparison against a strong framework baseline.
