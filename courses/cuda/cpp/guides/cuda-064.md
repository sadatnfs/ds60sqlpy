# cuda-064: Capstone: a custom ML operator that earns its existence

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-051`, `cuda-052`, `cuda-061`

The framework-binding part of this capstone also uses `cuda-097` (a Python API over a CUDA C++ operator) and `cuda-098` (backward as part of the operator) from the Python branch. They come later in the subject order, so read them before that part rather than treating them as a gate for opening this chapter.

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Capstone: a custom ML operator that earns its existence* with the concrete cases below. Finish with this evidence:
supported-contract documentation, forward and backward tests, invalid-input behavior, end-to-end measurement and an honest decision to keep or reject the custom kernel. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A custom ML operator has a forward contract and, when differentiable, a backward contract. State supported shape, strides, dtype, device, aliasing and stream behavior. Reject unsupported inputs before unsafe access. The operator must integrate with the framework's ownership and current-stream rules, not merely return plausible numbers. Compare against a readable framework reference and the framework's optimized or compiled path where available. Measure full training or inference scope, including backward, transfers and launch overhead. A faster forward kernel can still make training slower or produce wrong gradients.

## Mathematical contract

\[
\frac{\partial}{\partial x_i}\sum_j(a x_j+b)=a
\]

This derivative assumes a and b are constant with respect to the input. Parameter gradients require their own declared contract.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-064_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-064_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

For affine \(y=ax+b\) with a=3, b=1 and x=\([-1,0,2]\), forward output is \([-2,1,7]\). If a scalar loss sums outputs, each input gradient is three. A custom forward that returns the right values but backward returns one is mathematically wrong despite passing the forward fixture.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
x, a, b = [-1.0, 0.0, 2.0], 3.0, 1.0
forward = [a * value + b for value in x]
assert forward == [-2.0, 1.0, 7.0]


def loss(values):
    return sum(a * value + b for value in values)


epsilon = 1e-5
gradients = []
for i in range(len(x)):
    plus, minus = x.copy(), x.copy()
    plus[i] += epsilon
    minus[i] -= epsilon
    gradients.append((loss(plus) - loss(minus)) / (2 * epsilon))
assert all(abs(g - a) < 1e-8 for g in gradients)
print({"forward": forward, "CPU_finite_difference_gradients": gradients})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'forward': [-2.0, 1.0, 7.0], 'CPU_finite_difference_gradients': [3.000000000019653, 2.9999999999752442, 3.000000000064062]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For a fused bias-plus-ReLU, derivative at a nonzero preactivation is one when positive and zero when negative, multiplied by incoming gradient. The exact zero point needs the framework's chosen convention. A finite-difference check near a kink can be misleading, so test smooth points and the explicit boundary policy separately.

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

Compute input gradients for loss=sum(3*x+1).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A kernel assumes contiguous tensors but accepts transposed views. Diagnose it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an unsupported dtype do?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Define final acceptance for the custom operator.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **faster forward execution alone proves the operator improves training or is safe for arbitrary framework tensors.**

For the concrete failure exercise, a kernel assumes contiguous tensors but accepts transposed views. Diagnose it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-064_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-064: Capstone: a custom ML operator that earns its existence.
Read courses/cuda/cpp/guides/cuda-064.md and courses/cuda/cpp/lessons/cuda-064.md.
Direct prerequisites: `cuda-051`, `cuda-052`, `cuda-061`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-064_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-064_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
