# cuda-006: Numbers, units and a trustworthy answer

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain numbers, units and a trustworthy answer using the concrete cases below. Produce a testing policy specifying reference precision, tolerance and adversarial cases.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

Floating-point arithmetic stores a finite approximation to a real number. Adding a small quantity to a large one may round away the small quantity; subtracting similar large values can expose that loss. Relative error scales with a reference magnitude, while absolute error remains meaningful near zero. A common comparison accepts an error no larger than absolute tolerance plus relative tolerance times reference magnitude. The tolerances must come from input ranges, precision and the calculation, not from repeatedly widening them until a broken index passes. Check finite output explicitly, and use exact comparison for integer counts that cannot overflow.

## Mathematical contract

\[
|y-\widehat y|\leq\operatorname{atol}+\operatorname{rtol}|\widehat y|
\]

The observed value is y and the reference is y-hat. Require finite values unless exceptional outputs are explicitly part of the contract.

## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/cuda-006_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-006_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Compare output 0.00000004 with reference zero under absolute tolerance 0.0000001. It passes. A relative-only rule with zero reference would reject every nonzero result. Conversely, output 4 where reference is 3 cannot be excused as ordinary small rounding under those tolerances; first investigate shape, indexing and the mathematical contract.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Start with the literal input and intermediate quantities in worked example 1.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Identify exactly which condition changes in worked example 2.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 3

With \(\mathrm{atol}=0.001\) and \(\mathrm{rtol}=0.01\), find the allowed error at reference 20.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

A result contains NaN and a comparison test silently returns false. Repair the test.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

Why can signed 32-bit integer accumulation fail despite exact input values?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Design a histogram oracle.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **bitwise CPU/GPU equality is always necessary, or a loose tolerance makes any result acceptable. .**

For the concrete failure exercise, a result contains NaN and a comparison test silently returns false. Repair the test.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-006_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
