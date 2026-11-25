# cuda-006: Numbers, units and a trustworthy answer

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Write a testing policy that specifies reference precision, tolerances and adversarial floating-point cases.

**Scope:** Finite precision, integer overflow, floating-point reduction order, cancellation, absolute versus relative error, NaN/Inf and problem conditioning.

**Evidence to produce:** A testing policy specifying reference precision, tolerance and adversarial cases.

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

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-006_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-006_cpu.py
```

## Worked example 1: trace the mechanism

The exact sum of \([10^{16},1,-10^{16}]\) is 1. A sequential binary64 addition can return 0 because \(10^{16}+1\) rounds back to \(10^{16}\). Python's compensated `math.fsum` recovers 1 for this fixture. Different summation order is a numerical mechanism, not proof that either processor is faulty.

**Why:** Binary64 has a 53-bit significand, so near 1e16 the spacing is 2 and adding 1 is lost.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'sequential': 0.0, 'compensated_reference': 1.0}
```

**Check:** The reference asserts naive == 0.0 and math.fsum(values) == 1.0, printing sequential 0.0 and compensated 1.0.

## Worked example 2: change a meaningful condition

Compare output 0.00000004 with reference zero under absolute tolerance 0.0000001. It passes. A relative-only rule with zero reference would reject every nonzero result. Conversely, output 4 where reference is 3 cannot be excused as ordinary small rounding under those tolerances; first investigate shape, indexing and the mathematical contract.

**Why:** Absolute tolerance handles a zero reference, where relative error is undefined or infinite.

**Check:** The reference asserts abs(4e-8) <= 1e-7; also confirm |4 - 3| far exceeds any stated bound.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Trace the sum in order: 1e16 + 1 rounds to 1e16, then subtracting 1e16 leaves 0.0.

**Trap to avoid:** Blaming the processor for the zero ignores that the same order on any IEEE 754 machine gives 0.0.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Evaluate 4e-8 against atol 1e-7 with reference zero, then contrast with a relative-only rule.

**Trap to avoid:** Widening tolerance until output 4 matches reference 3 hides an indexing or contract bug as rounding.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

With \(\mathrm{atol}=0.001\) and \(\mathrm{rtol}=0.01\), find the allowed error at reference 20.

**Trap to avoid:** Using rtol alone gives 0.2 and rejects an output at error 0.2005 that the policy accepts.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A result contains NaN and a comparison test silently returns false. Repair the test.

**Trap to avoid:** Replacing NaN with zero before comparing hides the defect and can make a broken kernel pass.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why can signed 32-bit integer accumulation fail despite exact input values?

**Trap to avoid:** Switching to float32 avoids wrapping but loses exactness above 2^24, so counts become wrong.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a histogram oracle.

**Trap to avoid:** Comparing only the total misses a kernel that puts every value in the wrong bin but keeps the sum.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Bitwise CPU/GPU equality is always necessary, or a loose tolerance makes any result acceptable.** Parallel reductions legitimately change summation order, so bitwise equality is the wrong default; worked example 1 shows order alone turning 1 into 0. A tolerance must still be justified, because worked example 2 shows 4 against a reference of 3 is a real error, not rounding noise.

## Self-check, retrieval and transfer

1. Why does a relative-only tolerance fail at reference zero?
2. What does `math.fsum` demonstrate in worked example 1?
3. How should a test treat NaN in an output?

Short answers are in the [separate explanations](../solutions/cuda-006_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
