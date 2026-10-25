# cuda-052: explanatory solutions

## Mechanism review

Layer normalization centers a row by its mean and divides by a scale derived from variance; RMS normalization uses mean square without subtracting the mean. They are different operations. Epsilon stabilizes the denominator, but placing it inside versus outside a square root changes the formula. Fusion combines operations to avoid intermediates and launches. It can also increase registers, complicate reuse or prevent a good library path. Specify accumulation and output types, normalization axes and learned scale/bias if present. Compare both the mathematical contract and complete pipeline before claiming a fused kernel is better.

The separate [CPU reference](../references/cuda-052_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For row \([1,3]\), mean is two and population variance is one. With zero epsilon for this nondegenerate demonstration, centered normalized output is \([-1,1]\). RMS normalization instead divides \([1,3]\) by square root of five, giving different noncentered outputs.

## Exercise 2

For constant \([5,5]\), variance is zero. With positive epsilon inside the square root, centered output is \([0,0]\). A formula that omits epsilon divides zero by zero. Use this case to test stability, but also test low nonzero variance to detect an incorrectly placed epsilon.

## Exercise 3

First \([-1,2]\), then max with zero gives \([0,2]\). Fusion must preserve this operation order.

## Exercise 4

Dividing by n-1 changes the normalization contract. Match the framework/reference definition and axes.

## Exercise 5

Zero before any learned scale/bias, because the single value equals its mean and variance is zero.

## Exercise 6

It can avoid intermediate writes/reads and launches, while increasing live state/register pressure or restricting reuse. Measure both.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-052_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

It can avoid intermediate writes/reads and launches, while increasing live state/register pressure or restricting reuse. Measure both.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
