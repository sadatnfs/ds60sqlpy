# cuda-051: Softmax and reductions for model workloads

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-020`, `cuda-029`, `cuda-036`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Softmax and reductions for model workloads* with the concrete cases below. Finish with this evidence:
finite outputs, row sums within justified tolerance and comparison with the CPU reference. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Softmax converts a row of logits into nonnegative weights that sum to one. Exponentiating large logits directly can overflow even when the final probabilities are ordinary finite values. Subtracting the row maximum preserves the exact mathematical ratios while keeping the largest exponential at one. A kernel needs a maximum reduction, exponentials, a sum reduction and division, with correct row boundaries and accumulation precision. Define behavior for masks and exceptional inputs separately; an all-masked row cannot be treated as an ordinary finite row without a policy. Test short, ragged and extreme-valued rows.

## Mathematical contract

\[
p_i=\frac{e^{z_i-m}}{\sum_j e^{z_j-m}},\qquad m=\max_j z_j
\]

Subtracting one shared row maximum preserves ratios and prevents overflow from a large finite maximum. Exceptional/all-masked rows still need an explicit policy.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-051_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-051_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

For logits \([1000,1001]\), subtract maximum 1001 to obtain \([-1,0]\). Exponentials are approximately \([0.367879,1]\), giving probabilities \([0.268941,0.731059]\). Directly computing \(e^{1001}\) can overflow in common floating types although the normalized answer is well behaved.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
import math


def softmax(values):
    maximum = max(values)
    exp = [math.exp(v - maximum) for v in values]
    return [v / sum(exp) for v in exp]


p = softmax([1000, 1001])
assert abs(sum(p) - 1) < 1e-12 and abs(p[1] - 0.7310585786300049) < 1e-12
assert softmax([4, 4, 4]) == [1 / 3] * 3
print(p)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
[0.2689414213699951, 0.7310585786300049]
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For \([4,4,4]\), subtracting four produces three zeros, so each probability is one third. For a single finite logit, the output is one. These cases check normalization and row handling independently of large exponentials.

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

Compute softmax for \([0,0]\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A row sums to one but entries are in the wrong columns. Why is the test insufficient?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What must an all-masked attention row do?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a stable fused softmax contract.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **replacing the expression with a mathematically equivalent floating-point formula always preserves stability.**

For the concrete failure exercise, a row sums to one but entries are in the wrong columns. Why is the test insufficient?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-051_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-051: Softmax and reductions for model workloads.
Read courses/cuda/cpp/guides/cuda-051.md and courses/cuda/cpp/lessons/cuda-051.md.
Direct prerequisites: `cuda-020`, `cuda-029`, `cuda-036`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-051_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-051_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
