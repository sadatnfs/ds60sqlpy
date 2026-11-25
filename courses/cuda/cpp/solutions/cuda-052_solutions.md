# cuda-052: explanatory solutions

## Mechanism review

Layer normalization centers a row by its mean and divides by a scale derived from variance; RMS normalization uses mean square without subtracting the mean. They are different operations. Epsilon stabilizes the denominator, but placing it inside versus outside a square root changes the formula. Fusion combines operations to avoid intermediates and launches. It can also increase registers, complicate reuse or prevent a good library path. Specify accumulation and output types, normalization axes and learned scale/bias if present. Compare both the mathematical contract and complete pipeline before claiming a fused kernel is better.

## Exercise 1

For row \([1,3]\), mean is two and population variance is one. With zero epsilon for this nondegenerate demonstration, centered normalized output is \([-1,1]\). RMS normalization instead divides \([1,3]\) by square root of five, giving different noncentered outputs.

**Approach:** Center [1, 3] at mean 2, divide by population standard deviation 1, then compute RMS normalization separately.

**Why it is correct:** Layer normalization gives [-1, 1], while RMS divides by sqrt((1 + 9) / 2) = sqrt(5).

**A plausible wrong approach:** Treating RMS normalization as layer normalization without centering returns different values.

**How to verify:** The reference asserts normalized == [-1.0, 1.0] and prints the RMS denominator sqrt(5).

## Exercise 2

For constant \([5,5]\), variance is zero. With positive epsilon inside the square root, centered output is \([0,0]\). A formula that omits epsilon divides zero by zero. Use this case to test stability, but also test low nonzero variance to detect an incorrectly placed epsilon.

**Approach:** Add a positive epsilon inside the square root before dividing.

**Why it is correct:** For [5, 5] the variance is 0, centering gives zeros, and epsilon keeps the denominator positive.

**A plausible wrong approach:** Omitting epsilon divides 0 by 0 and yields NaN for a constant row.

**How to verify:** Test [5, 5] for [0, 0] output and a low-variance row for finite results.

## Exercise 3

First \([-1,2]\), then max with zero gives \([0,2]\). Fusion must preserve this operation order.

**Approach:** Add bias 1 to [-2, 1] for [-1, 2], then apply max with zero.

**Why it is correct:** ReLU zeroes the negative entry, giving [0, 2].

**A plausible wrong approach:** Applying ReLU before bias gives [1, 2], a different operation order.

**How to verify:** The reference asserts [max(0, x + 1) for x in [-2, 1]] == [0, 2].

## Exercise 4

Dividing by n-1 changes the normalization contract. Match the framework/reference definition and axes.

**Approach:** Divide by n instead of n minus one to match the framework's normalization.

**Why it is correct:** Layer normalization uses population variance over the normalized axes.

**A plausible wrong approach:** Using sample variance changes every output slightly and drifts from the reference.

**How to verify:** Compare outputs on [1, 3] against the framework for the same axes.

## Exercise 5

Zero before any learned scale/bias, because the single value equals its mean and variance is zero.

**Approach:** Center the single value at its own mean and divide by sqrt(epsilon).

**Why it is correct:** The centered value is zero, so the output is zero before scale and bias.

**A plausible wrong approach:** Skipping normalization for singletons returns the raw value instead of zero.

**How to verify:** Assert the output for [7] is [0] with positive epsilon.

## Exercise 6

It can avoid intermediate writes/reads and launches, while increasing live state/register pressure or restricting reuse. Measure both.

**Approach:** Count avoided intermediate reads and writes against added register pressure.

**Why it is correct:** Fusion removes a round trip to memory but keeps more values live per thread.

**A plausible wrong approach:** Fusing everything by default can cause spills and slow the kernel.

**How to verify:** Measure fused and separate versions and check spill reports.

## Self-check answers

1. **What does fused bias-plus-ReLU give for x = [-2,1] and bias 1?** [0,2]: the biased values are [-1,2] and ReLU clamps the negative one to zero.
2. **What variance does sample variance give for [1,3], and what is the effect?** 2 instead of the population value 1, so outputs shrink by a factor of the square root of 2.
3. **What is centered normalization of a single value with positive epsilon?** [0], because the value minus its own mean is zero and epsilon keeps the denominator positive.

## Numerical reference and its limits

The [CPU reference](../references/cuda-052_cpu.py) reproduces worked example 1 and prints `{'layer_normalized': [-1.0, 1.0], 'RMS_denominator': 2.23606797749979}`.

## Transfer review

It can avoid intermediate writes/reads and launches, while increasing live state/register pressure or restricting reuse. Measure both.
