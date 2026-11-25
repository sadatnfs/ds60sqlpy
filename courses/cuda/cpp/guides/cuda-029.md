# cuda-029: Floating point under optimization

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-020`, `cuda-025`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Document an accepted error policy and measure numerical differences under reviewed compiler options such as fast math.

**Scope:** Fused multiply-add, accumulation precision, fast-math tradeoffs, denormals, condition number, reproducibility and deterministic algorithms.

**Evidence to produce:** A documented policy for accepted error and rejected non-finite output, plus measured differences under reviewed compiler configurations.

## Purpose, vocabulary and mental model

A mathematically equivalent expression can have different floating-point behavior. Fused multiply-add rounds a product-plus-sum once instead of rounding the product and then the addition. Fast-math modes can change precision and special-value behavior, so they require an explicit error budget. Variance computed as mean of squares minus square of mean subtracts nearby large values and can lose a small real variance. A centered or carefully merged online algorithm reduces that risk. Conditioning describes sensitivity of the problem itself; algorithmic stability describes how well the chosen computation handles it. Neither is fixed merely by changing processors.

### Key terms

- **Fused multiply-add (FMA):** An operation that computes a*b+c with a single rounding instead of two.
- **Fast math:** Compiler options such as `--use_fast_math` that trade precision and special-value handling for speed.
- **Welford's algorithm:** An online method for mean and variance that avoids subtracting large, nearly equal sums.
- **Error budget:** The documented maximum deviation from a reference that a result may show and still be accepted.

## Mathematical contract

\[
\mu=\frac{1}{n}\sum_i x_i,\qquad v=\frac{1}{n}\sum_i(x_i-\mu)^2
\]

This is population variance for nonempty data. Centering reduces cancellation relative to subtracting two large nearly equal moments, but does not make all rounding disappear.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-029_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-029_cpu.py
```

## Worked example 1: trace the mechanism

For \([100000001,100000002,100000003]\), center around the mean 100000002. Squared deviations are \([1,0,1]\), giving population variance \(\frac{2}{3}\). Computing two roughly \(10^{16}\) quantities and subtracting them risks losing that small answer in ordinary floating precision.

**Why:** Centered squares are [1, 0, 1], small numbers whose average 2 / 3 is computed exactly enough.

```python
import math

values = [100000001.0, 100000002.0, 100000003.0]
mean = math.fsum(values) / len(values)
variance = math.fsum((x - mean) ** 2 for x in values) / len(values)
assert variance == 2 / 3
assert math.fsum((x - 2) ** 2 for x in [2, 2, 2]) == 0
print({"mean": mean, "centered_population_variance": variance})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'mean': 100000002.0, 'centered_population_variance': 0.6666666666666666}
```

**Check:** The reference asserts variance == 2 / 3 using math.fsum with the centered formula.

## Worked example 2: change a meaningful condition

A dot product with very large and very small terms can differ under different association or FMA choices. Compare to a higher-precision reference and report absolute error, relative error when meaningful, and nonfinite values. Exact equality is appropriate only when the contract and arithmetic justify it.

**Why:** FMA and reassociation change rounding, so two valid results can differ in low bits.

**Check:** Check every output is finite and the error is within a declared tolerance.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Subtract the mean 100000002 from each value before squaring, giving deviations -1, 0 and 1.

**Trap to avoid:** Using E[x^2] minus E[x]^2 subtracts two numbers near 1e16 and loses the small difference in rounding.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Compare the dot product with a higher-precision reference and report absolute and relative error.

**Trap to avoid:** Demanding bitwise equality with a CPU loop rejects valid optimized results and passes nothing new.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute population variance of \([2,2,2]\).

**Trap to avoid:** Dividing by the standard deviation next without a policy gives division by zero.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A faster compiler mode changes a near-zero result. What decides acceptability?

**Trap to avoid:** Accepting any new value because the mode is faster leaves the error unbounded.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why can relative error explode near zero?

**Trap to avoid:** Reporting only relative error marks near-zero outputs as wildly wrong.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose a reduction policy for a scientific report.

**Trap to avoid:** Switching to fast-math between baseline and candidate benchmarks mixes numerical and speed changes.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A faster approximate operation is an interchangeable implementation for every application.** Fast-math and reassociation change rounding, special values and sometimes accuracy by large factors, as the cancellation in worked example 1 shows. Whether that is acceptable depends on an error budget for the application, so a faster mode must be measured against a higher-precision reference before it replaces the original.

## Self-check, retrieval and transfer

1. Why does centering around the mean help in worked example 1?
2. What does FMA change compared with a separate multiply and add?
3. When is exact equality an appropriate test for floating point?

Short answers are in the [separate explanations](../solutions/cuda-029_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-029: Floating point under optimization.
Read courses/cuda/cpp/guides/cuda-029.md and courses/cuda/cpp/lessons/cuda-029.md.
Direct prerequisites: `cuda-006`, `cuda-020`, `cuda-025`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-029_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-029_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
