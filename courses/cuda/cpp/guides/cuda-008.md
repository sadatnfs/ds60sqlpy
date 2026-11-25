# cuda-008: Reproducibility, safety and the first evidence notebook

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-003`, `cuda-006`, `cuda-007`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Create a reusable experiment template that records inputs, environment, timing scope and capability status.

**Scope:** Record input generation, seed, shape, dtype, hardware, software, launch parameters, warm-up, repetitions and timing scope.

**Evidence to produce:** A reusable experiment template and correctly labeled capability status.

## Purpose, vocabulary and mental model

A reproducible experiment records enough context to explain why a result happened. An input seed is useful only alongside the generator, dtype, shape and distribution. A benchmark needs timing scope, warm-up policy and retained samples, while a correctness result needs an independent expected answer. Hardware access, successful compilation, successful execution and acceptable numerical output are four distinct observations. A resource budget limits input size and repeated work before running. On a shared GPU, reserve only the memory and compute time that the owner has authorized; do not use unbounded spin loops as teaching fixtures.

### Key terms

- **Random seed:** The initial value for a pseudorandom generator, meaningful only together with the generator, dtype, shape and distribution.
- **Warm-up run:** An untimed execution that absorbs one-time initialization or JIT costs before repeated measurements.
- **Timing scope:** The exact set of operations, such as kernel only or end to end, that a measurement includes.
- **Capability status:** A labeled record of which observations exist, such as compiled, executed on a GPU or validated numerically.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-008_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-008_cpu.py
```

## Worked example 1: trace the mechanism

Report A says 'GPU: 0.2 ms'. Report B records a synthetic float32 vector of 1,024 elements, seed 7, upload excluded, five warm-ups, twenty event-timed samples, device/toolkit identities and an absolute error bound. B is interpretable, but it still needs raw samples and CPU comparison before supporting a speedup claim.

**Why:** Each field lets another person reproduce the run or judge its scope; 0.2 ms alone cannot be interpreted.

```python
x, y = [0, -2, 5], [3, 2, -1]
assert [a + b for a, b in zip(x, y)] == [3, 0, 4]
receipt = {"surface": "CPU reference", "shape": [3], "result": [3, 0, 4], "gpu_executed": False}
print(receipt)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'surface': 'CPU reference', 'shape': [3], 'result': [3, 0, 4], 'gpu_executed': False}
```

**Check:** Check each field of B against the receipt template and mark raw samples and CPU comparison as missing.

## Worked example 2: change a meaningful condition

A vector-add oracle uses \([0,-2,5]\) and \([3,2,-1]\), expecting \([3,0,4]\). Add length-zero and a 33-element fixture to expose assumptions about block boundaries. This reference can run on any CPU. Label it CPU correctness evidence rather than evidence that a GPU kernel has run.

**Why:** Negative and zero results exercise signs, and 33 elements cross a 32-thread boundary into a second warp.

**Check:** The reference asserts the sum is [3, 0, 4] and prints a receipt with gpu_executed False.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. List what Report B records that Report A lacks: data type, size, seed, warm-ups, sample count, identities and an error bound.

**Trap to avoid:** Treating B as proof of speedup ignores that it still lacks raw samples and a matched CPU baseline.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Add [0, -2, 5] and [3, 2, -1] elementwise, then extend fixtures to length 0 and 33.

**Trap to avoid:** Testing only with 32 elements would pass a kernel that drops or overruns the tail element.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Write five required fields for a correctness receipt.

**Trap to avoid:** Recording only pass or fail discards the observed values that would reveal a near-miss or a tolerance problem.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A run was cancelled but marked passed because the compiler exited zero. Correct the record.

**Trap to avoid:** Leaving passed because no error appeared conflates missing evidence with positive evidence.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How should a no-device run be represented?

**Trap to avoid:** Substituting the CPU reference output and labeling it CUDA invents execution evidence that never existed.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a memory budget for three float32 vectors of one million elements.

**Trap to avoid:** Budgeting exactly 12 MB of free memory fails when the runtime context and alignment add their own usage.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A screenshot of a timing or a driver version is sufficient runtime evidence.** A screenshot cannot show the input, timing scope, warm-up policy or correctness check behind a number. Worked example 1 contrasts a bare 0.2 ms claim with a record of shape, seed, warm-ups, samples, versions and an error bound; only the second can be checked or reproduced by someone else.

## Self-check, retrieval and transfer

1. Which four observations must stay separate in a receipt?
2. Why does a seed alone not reproduce an input?
3. Why add a 33-element fixture to the vector-add oracle?

Short answers are in the [separate explanations](../solutions/cuda-008_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-008: Reproducibility, safety and the first evidence notebook.
Read courses/cuda/cpp/guides/cuda-008.md and courses/cuda/cpp/lessons/cuda-008.md.
Direct prerequisites: `cuda-003`, `cuda-006`, `cuda-007`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-008_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-008_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
