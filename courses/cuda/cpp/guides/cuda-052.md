# cuda-052: Normalization, fusion and memory traffic

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-019`, `cuda-029`, `cuda-034`, `cuda-051`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Compare fused and unfused normalization kernels on error, bytes moved, launch count and measured time.

**Scope:** Mean/variance versus RMS normalization, epsilon semantics, accumulation precision, fused elementwise work and reduction limits.

**Evidence to produce:** An error-budgeted result plus measured bytes/launch reduction and an honest performance comparison.

## Purpose, vocabulary and mental model

Layer normalization centers a row by its mean and divides by a scale derived from variance; RMS normalization uses mean square without subtracting the mean. They are different operations. Epsilon stabilizes the denominator, but placing it inside versus outside a square root changes the formula. Fusion combines operations to avoid intermediates and launches. It can also increase registers, complicate reuse or prevent a good library path. Specify accumulation and output types, normalization axes and learned scale/bias if present. Compare both the mathematical contract and complete pipeline before claiming a fused kernel is better.

### Key terms

- **Layer normalization:** Rescaling each row to zero mean and unit variance, then applying learned scale and shift.
- **RMS normalization:** Rescaling each row by its root mean square without subtracting the mean.
- **Kernel fusion:** Combining steps into one kernel so intermediate values stay on chip instead of round-tripping through global memory.
- **Epsilon:** A small constant added to a variance or mean square so normalization never divides by zero.

## Mathematical contract

\[
y_i=\frac{x_i-\mu}{\sqrt{v+\epsilon}}
\]

This centered population normalization puts epsilon inside the square root. RMS normalization and epsilon outside the root are different formulas.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-052_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-052_cpu.py
```

## Worked example 1: trace the mechanism

For row \([1,3]\), mean is two and population variance is one. With zero epsilon for this nondegenerate demonstration, centered normalized output is \([-1,1]\). RMS normalization instead divides \([1,3]\) by square root of five, giving different noncentered outputs.

**Why:** Layer normalization gives [-1, 1], while RMS divides by sqrt((1 + 9) / 2) = sqrt(5).

```python
import math

row = [1.0, 3.0]
mean = sum(row) / len(row)
variance = sum((x - mean) ** 2 for x in row) / len(row)
normalized = [(x - mean) / math.sqrt(variance) for x in row]
assert normalized == [-1.0, 1.0]
assert [max(0, x + 1) for x in [-2, 1]] == [0, 2]
print({"layer_normalized": normalized, "RMS_denominator": math.sqrt(5)})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'layer_normalized': [-1.0, 1.0], 'RMS_denominator': 2.23606797749979}
```

**Check:** The reference asserts normalized == [-1.0, 1.0] and prints the RMS denominator sqrt(5).

## Worked example 2: change a meaningful condition

For constant \([5,5]\), variance is zero. With positive epsilon inside the square root, centered output is \([0,0]\). A formula that omits epsilon divides zero by zero. Use this case to test stability, but also test low nonzero variance to detect an incorrectly placed epsilon.

**Why:** For [5, 5] the variance is 0, centering gives zeros, and epsilon keeps the denominator positive.

**Check:** Test [5, 5] for [0, 0] output and a low-variance row for finite results.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Center [1, 3] at mean 2, divide by population standard deviation 1, then compute RMS normalization separately.

**Trap to avoid:** Treating RMS normalization as layer normalization without centering returns different values.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Add a positive epsilon inside the square root before dividing.

**Trap to avoid:** Omitting epsilon divides 0 by 0 and yields NaN for a constant row.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute fused bias-plus-ReLU for x=\([-2,1]\), bias=1.

**Trap to avoid:** Applying ReLU before bias gives [1, 2], a different operation order.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

An implementation uses sample variance instead of population variance. Diagnose it.

**Trap to avoid:** Using sample variance changes every output slightly and drifts from the reference.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What is the singleton centered normalization with positive epsilon?

**Trap to avoid:** Skipping normalization for singletons returns the raw value instead of zero.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Estimate one benefit and one cost of fusion.

**Trap to avoid:** Fusing everything by default can cause spills and slow the kernel.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Fusion is always faster or the same epsilon convention is interchangeable across formulas.** Fusion removes intermediate traffic and launches but can raise register pressure or block reuse, so it must be measured. Epsilon conventions are not interchangeable either: adding it inside the square root differs from adding it to the denominator. Match the reference formula exactly and test constant and low variance rows.

## Self-check, retrieval and transfer

1. What does fused bias-plus-ReLU give for x = [-2,1] and bias 1?
2. What variance does sample variance give for [1,3], and what is the effect?
3. What is centered normalization of a single value with positive epsilon?

Short answers are in the [separate explanations](../solutions/cuda-052_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-052: Normalization, fusion and memory traffic.
Read courses/cuda/cpp/guides/cuda-052.md and courses/cuda/cpp/lessons/cuda-052.md.
Direct prerequisites: `cuda-019`, `cuda-029`, `cuda-034`, `cuda-051`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-052_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-052_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
