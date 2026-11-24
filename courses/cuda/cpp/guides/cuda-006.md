# cuda-006: Numbers, units and a trustworthy answer

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Write a testing policy that specifies reference precision, tolerances and adversarial floating-point cases.

Work through *Numbers, units and a trustworthy answer* with the concrete cases below. Finish with this evidence:
a testing policy specifying reference precision, tolerance and adversarial cases. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Floating-point arithmetic stores a finite approximation to a real number. Adding a small quantity to a large one may round away the small quantity; subtracting similar large values can expose that loss. Relative error scales with a reference magnitude, while absolute error remains meaningful near zero. A common comparison accepts an error no larger than absolute tolerance plus relative tolerance times reference magnitude. The tolerances must come from input ranges, precision and the calculation, not from repeatedly widening them until a broken index passes. Check finite output explicitly, and use exact comparison for integer counts that cannot overflow.

### Key terms

- **Relative error:** The absolute difference from a reference divided by the reference magnitude, which is meaningful away from zero.
- **Absolute tolerance:** A fixed allowed difference that keeps a comparison meaningful for values near zero.
- **Catastrophic cancellation:** The loss of significant digits when two nearly equal rounded values are subtracted.
- **Conditioning:** How strongly the exact answer changes when the input changes slightly, independent of the algorithm.
- **NaN:** A floating-point not-a-number value produced by invalid operations, which compares unequal even to itself.

## Mathematical contract

\[
|y-\widehat y|\leq\operatorname{atol}+\operatorname{rtol}|\widehat y|
\]

The observed value is y and the reference is y-hat. Require finite values unless exceptional outputs are explicitly part of the contract.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-006_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-006_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

The exact sum of \([10^{16},1,-10^{16}]\) is 1. A sequential binary64 addition can return 0 because \(10^{16}+1\) rounds back to \(10^{16}\). Python's compensated `math.fsum` recovers 1 for this fixture. Different summation order is a numerical mechanism, not proof that either processor is faulty.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
import math

values = [1e16, 1.0, -1e16]
naive = 0.0
for value in values:
    naive += value
assert naive == 0.0 and math.fsum(values) == 1.0
assert abs(4e-8) <= 1e-7
print({"sequential": naive, "compensated_reference": math.fsum(values)})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'sequential': 0.0, 'compensated_reference': 1.0}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Compare output 0.00000004 with reference zero under absolute tolerance 0.0000001. It passes. A relative-only rule with zero reference would reject every nonzero result. Conversely, output 4 where reference is 3 cannot be excused as ordinary small rounding under those tolerances; first investigate shape, indexing and the mathematical contract.

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

With \(\mathrm{atol}=0.001\) and \(\mathrm{rtol}=0.01\), find the allowed error at reference 20.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A result contains NaN and a comparison test silently returns false. Repair the test.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why can signed 32-bit integer accumulation fail despite exact input values?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a histogram oracle.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **bitwise CPU/GPU equality is always necessary, or a loose tolerance makes any result acceptable. .**

For the concrete failure exercise, a result contains NaN and a comparison test silently returns false. Repair the test.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-006_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [Numerical background](https://docs.nvidia.com/cuda/floating-point/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-006: Numbers, units and a trustworthy answer.
Read courses/cuda/cpp/guides/cuda-006.md and courses/cuda/cpp/lessons/cuda-006.md.
Direct prerequisites: `cuda-005`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-006_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-006_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
