# cuda-064: Capstone: a custom ML operator that earns its existence

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-051`, `cuda-052`, `cuda-061`

The framework-binding part of this capstone also uses `cuda-097` (a Python API over a CUDA C++ operator) and `cuda-098` (backward as part of the operator) from the Python branch. They come later in the subject order, so read them before that part rather than treating them as a gate for opening this chapter.

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a custom ML operator with forward and backward tests, input validation and an end-to-end keep or reject decision.

**Scope:** Custom kernels versus existing framework operations, forward/backward contracts, shapes, strides, dtypes, devices, stream semantics, error propagation, packaging and regression coverage.

**Evidence to produce:** Supported-contract documentation, forward and backward tests, invalid-input behavior, end-to-end measurement and an honest decision to keep or reject the custom kernel.

## Purpose, vocabulary and mental model

A custom ML operator has a forward contract and, when differentiable, a backward contract. State supported shape, strides, dtype, device, aliasing and stream behavior. Reject unsupported inputs before unsafe access. The operator must integrate with the framework's ownership and current-stream rules, not merely return plausible numbers. Compare against a readable framework reference and the framework's optimized or compiled path where available. Measure full training or inference scope, including backward, transfers and launch overhead. A faster forward kernel can still make training slower or produce wrong gradients.

### Key terms

- **Forward contract:** The documented shapes, dtypes, devices and layouts that an operator accepts and returns.
- **Backward pass:** The computation of input gradients from output gradients that training frameworks require.
- **Gradient check:** Comparing analytic gradients with finite-difference estimates at chosen points.
- **Current stream:** The framework's active CUDA stream, which a custom operator must launch on to keep ordering correct.

## Mathematical contract

\[
\frac{\partial}{\partial x_i}\sum_j(a x_j+b)=a
\]

This derivative assumes a and b are constant with respect to the input. Parameter gradients require their own declared contract.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-064_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-064_cpu.py
```

## Worked example 1: trace the mechanism

For affine \(y=ax+b\) with a=3, b=1 and x=\([-1,0,2]\), forward output is \([-2,1,7]\). If a scalar loss sums outputs, each input gradient is three. A custom forward that returns the right values but backward returns one is mathematically wrong despite passing the forward fixture.

**Why:** Forward gives [-2, 1, 7], and each input gradient of sum(3x + 1) is the slope 3.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'forward': [-2.0, 1.0, 7.0], 'CPU_finite_difference_gradients': [3.000000000019653, 2.9999999999752442, 3.000000000064062]}
```

**Check:** The reference asserts forward == [-2.0, 1.0, 7.0] and every finite-difference gradient within 1e-8 of 3.

## Worked example 2: change a meaningful condition

For a fused bias-plus-ReLU, derivative at a nonzero preactivation is one when positive and zero when negative, multiplied by incoming gradient. The exact zero point needs the framework's chosen convention. A finite-difference check near a kink can be misleading, so test smooth points and the explicit boundary policy separately.

**Why:** ReLU's derivative is a step, so the mask selects which gradients pass.

**Check:** Test points away from zero numerically, and check the zero convention against the framework.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Compute forward 3x + 1 on [-1, 0, 2], then check gradients of the summed loss with central finite differences.

**Trap to avoid:** A backward pass returning 1 passes every forward test while giving wrong gradients to training.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Multiply the incoming gradient by 1 for positive preactivations and 0 for negative ones.

**Trap to avoid:** Finite-differencing exactly at zero straddles the kink and gives one half.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute input gradients for loss=sum(3*x+1).

**Trap to avoid:** Returning the forward values as gradients confuses outputs with derivatives.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A kernel assumes contiguous tensors but accepts transposed views. Diagnose it.

**Trap to avoid:** Indexing as contiguous reads elements in the wrong order.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an unsupported dtype do?

**Trap to avoid:** Silently casting can change precision and results.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Define final acceptance for the custom operator.

**Trap to avoid:** Accepting it on speed alone ignores correctness and maintenance.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Faster forward execution alone proves the operator improves training or is safe for arbitrary framework tensors.** A faster forward pass says nothing about gradients, strides, dtypes or stream rules. Worked example 1 shows correct outputs paired with a wrong gradient of one. Accept the operator only after forward and backward checks pass and unsupported tensors are rejected.

## Self-check, retrieval and transfer

1. What are the input gradients for loss = sum(3x+1)?
2. A kernel assumes contiguous tensors but accepts transposed views. What is wrong?
3. What should an unsupported dtype do?

Short answers are in the [separate explanations](../solutions/cuda-064_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
