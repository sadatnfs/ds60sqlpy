# cuda-064: explanatory solutions

## Mechanism review

A custom ML operator has a forward contract and, when differentiable, a backward contract. State supported shape, strides, dtype, device, aliasing and stream behavior. Reject unsupported inputs before unsafe access. The operator must integrate with the framework's ownership and current-stream rules, not merely return plausible numbers. Compare against a readable framework reference and the framework's optimized or compiled path where available. Measure full training or inference scope, including backward, transfers and launch overhead. A faster forward kernel can still make training slower or produce wrong gradients.

The separate [CPU reference](../references/cuda-064_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For affine y=a*x+b with a=3, b=1 and x=\([-1,0,2]\), forward output is \([-2,1,7]\). If a scalar loss sums outputs, each input gradient is three. A custom forward that returns the right values but backward returns one is mathematically wrong despite passing the forward fixture.

## Exercise 2

For a fused bias-plus-ReLU, derivative at a nonzero preactivation is one when positive and zero when negative, multiplied by incoming gradient. The exact zero point needs the framework's chosen convention. A finite-difference check near a kink can be misleading, so test smooth points and the explicit boundary policy separately.

## Exercise 3

Every component is three. Also test parameter gradients if a and b are learnable in the declared interface.

## Exercise 4

Either implement stride-aware indexing, make an explicit accounted copy or reject unsupported layouts; do not reinterpret shape as contiguity.

## Exercise 5

Raise a clear validation error before launch or select a documented fallback; never cast silently if it changes the operator contract.

## Exercise 6

Forward/reference parity, backward checks, boundary and invalid-input tests, stream/lifetime correctness, real GPU evidence when claimed and end-to-end comparison against a strong framework baseline.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-064_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Forward/reference parity, backward checks, boundary and invalid-input tests, stream/lifetime correctness, real GPU evidence when claimed and end-to-end comparison against a strong framework baseline.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
