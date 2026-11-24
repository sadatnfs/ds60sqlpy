# cuda-029: Floating point under optimization

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-020`, `cuda-025`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Document an accepted error policy and measure numerical differences under reviewed compiler options such as fast math.

Work through *Floating point under optimization* with the concrete cases below. Finish with this evidence:
a documented policy for accepted error and rejected non-finite output, plus measured differences under reviewed compiler configurations. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

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

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-029_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-029_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

For \([100000001,100000002,100000003]\), center around the mean 100000002. Squared deviations are \([1,0,1]\), giving population variance \(\frac{2}{3}\). Computing two roughly \(10^{16}\) quantities and subtracting them risks losing that small answer in ordinary floating precision.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
import math

values = [100000001.0, 100000002.0, 100000003.0]
mean = math.fsum(values) / len(values)
variance = math.fsum((x - mean) ** 2 for x in values) / len(values)
assert variance == 2 / 3
assert math.fsum((x - 2) ** 2 for x in [2, 2, 2]) == 0
print({"mean": mean, "centered_population_variance": variance})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'mean': 100000002.0, 'centered_population_variance': 0.6666666666666666}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A dot product with very large and very small terms can differ under different association or FMA choices. Compare to a higher-precision reference and report absolute error, relative error when meaningful, and nonfinite values. Exact equality is appropriate only when the contract and arithmetic justify it.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

Exercises 1 and 2 are guided reconstructions of the worked examples; exercises
3-6 change an input, diagnose a defect, test a boundary and transfer the idea.
For each one, keep the calculation, output, diagram or failure policy you
produce so another reader can compare it with the worked cases. If the hint is
not enough, reread the mechanism paragraph and the bounded CPU assertion.

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute population variance of \([2,2,2]\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A faster compiler mode changes a near-zero result. What decides acceptability?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why can relative error explode near zero?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose a reduction policy for a scientific report.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a faster approximate operation is an interchangeable implementation for every application.**

For the concrete failure exercise, a faster compiler mode changes a near-zero result. What decides acceptability?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-029_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
