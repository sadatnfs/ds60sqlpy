# cuda-063: Capstone: a measured scientific or data application

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-038`, `cuda-039`, `cuda-040`, `cuda-044`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Deliver a measured scientific application with a CPU baseline, adversarial tests, profiling artifacts and a reproducible benchmark.

**Scope:** Requirements, numerical specification, correctness oracle, resource budget, profile-guided optimization and communication of tradeoffs.

**Evidence to produce:** CPU baseline, adversarial tests, sanitizer results where applicable, profiling artifacts, reproducible benchmark, failure behavior and a report stating when CPU is preferable.

## Purpose, vocabulary and mental model

An independent numerical project begins with a bounded question, not a performance claim. Specify accepted input, output semantics, precision, resource budget and failure behavior. Build an independent CPU reference and adversarial fixtures before optimizing. Choose algorithms or libraries that fit the contract, then profile the complete pipeline. Retain evidence that another learner can reproduce: source, generation parameters, correctness comparisons, tool diagnostics where available and timing samples. A CPU-only project remains a valid algorithm/design portfolio piece when it clearly leaves GPU performance unmeasured.

### Key terms

- **Research question:** The specific, measurable question that the application and its benchmark are designed to answer.
- **Reproducible benchmark:** A measurement that another person can rerun from recorded code, inputs, environment and procedure.
- **Profiling artifact:** A saved profiler report or timeline that supports a stated performance claim.
- **CPU preference boundary:** The problem size or condition below which the CPU version is the better choice.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-063_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-063_cpu.py
```

## Worked example 1: trace the mechanism

Project A filters a synthetic signal with a fixed-zero stencil, computes an energy sum and returns both transformed values and the scalar. For \([2,4,8]\), the stencil reference is \([2,\frac{14}{3},4]\). The energy is the sum of squares, \(\frac{376}{9}\). Explicitly define whether energy is computed before or after filtering.

**Why:** The middle value averages 2, 4 and 8 to 14/3, and edges average with zero, giving energy 376/9.

```python
from fractions import Fraction

filtered = [Fraction(2), Fraction(14, 3), Fraction(4)]
energy = sum(x * x for x in filtered)
assert energy == Fraction(376, 9)
print({"exact_filtered": [str(x) for x in filtered], "post_filter_energy": str(energy)})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'exact_filtered': ['2', '14/3', '4'], 'post_filter_energy': '376/9'}
```

**Check:** The reference asserts energy == Fraction(376, 9) and prints the exact filtered values.

## Worked example 2: change a meaningful condition

Project B aggregates graph neighbors using CSR then normalizes nonempty rows. It includes isolated nodes, duplicate-edge policy and skewed row lengths. The project can choose a library sparse multiply or a custom kernel, but must compare identical semantics and include conversion costs when the graph arrives in another format.

**Why:** Isolated nodes have no neighbors, so skipping their normalization avoids dividing by zero.

**Check:** Include isolated nodes, duplicates and skewed rows, and compare against a host reference.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Apply the fixed-zero stencil to [2, 4, 8], then square and sum the filtered values with exact fractions.

**Trap to avoid:** Computing energy on the unfiltered signal returns 84, a different quantity than the contract asks for.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Build CSR from edges, aggregate neighbors, then normalize only rows with nonzero degree.

**Trap to avoid:** Normalizing every row divides isolated rows by zero and spreads NaN.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Write a minimal acceptance contract for Project A.

**Trap to avoid:** Checking only the energy scalar lets filter errors cancel and pass.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A project claims a speedup but omits graph conversion. Diagnose it.

**Trap to avoid:** Timing only the kernel overstates speedup.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Give three adversarial fixtures.

**Trap to avoid:** Testing only typical sizes misses failures at edges.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Decide whether the GPU earns deployment.

**Trap to avoid:** Deploying because the kernel is faster ignores total cost.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A performance demo without documented assumptions is a deliverable someone else can maintain.** A demo without its assumptions cannot be rerun, checked or extended by anyone else. A deliverable states its input contract, precision, resource budget, failure behavior and reference, and keeps source, generators, commands and raw measurements. Report end-to-end time, including conversions such as building CSR, beside kernel time. For Project A the reference is concrete: input [2,4,8] gives stencil output [2, 14/3, 4] and energy 376/9, so any GPU path must match both.

## Self-check, retrieval and transfer

1. What energy does Project A give for the stencil output [2, 14/3, 4]?
2. A speedup claim omits graph conversion. Why does that matter?
3. Name three adversarial fixtures for Project B.

Short answers are in the [separate explanations](../solutions/cuda-063_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-063: Capstone: a measured scientific or data application.
Read courses/cuda/cpp/guides/cuda-063.md and courses/cuda/cpp/lessons/cuda-063.md.
Direct prerequisites: `cuda-038`, `cuda-039`, `cuda-040`, `cuda-044`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-063_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-063_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
