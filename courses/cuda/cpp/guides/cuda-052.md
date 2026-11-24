# cuda-052: Normalization, fusion and memory traffic

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-019`, `cuda-029`, `cuda-034`, `cuda-051`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Compare fused and unfused normalization kernels on error, bytes moved, launch count and measured time.

Work through *Normalization, fusion and memory traffic* with the concrete cases below. Finish with this evidence:
an error-budgeted result plus measured bytes/launch reduction and an honest performance comparison. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

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

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-052_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-052_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

For row \([1,3]\), mean is two and population variance is one. With zero epsilon for this nondegenerate demonstration, centered normalized output is \([-1,1]\). RMS normalization instead divides \([1,3]\) by square root of five, giving different noncentered outputs.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

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

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'layer_normalized': [-1.0, 1.0], 'RMS_denominator': 2.23606797749979}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For constant \([5,5]\), variance is zero. With positive epsilon inside the square root, centered output is \([0,0]\). A formula that omits epsilon divides zero by zero. Use this case to test stability, but also test low nonzero variance to detect an incorrectly placed epsilon.

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

Compute fused bias-plus-ReLU for x=\([-2,1]\), bias=1.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

An implementation uses sample variance instead of population variance. Diagnose it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What is the singleton centered normalization with positive epsilon?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Estimate one benefit and one cost of fusion.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **fusion is always faster or the same epsilon convention is interchangeable across formulas.**

For the concrete failure exercise, an implementation uses sample variance instead of population variance. Diagnose it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-052_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
