# cuda-058: CUTLASS, CuTe and tile abstractions

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-019`, `cuda-046`, `cuda-053`, `cuda-056`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *CUTLASS, CuTe and tile abstractions* with the concrete cases below. Finish with this evidence:
correct layouts, supported feature declaration and benchmark against an appropriate library baseline. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

CUTLASS supplies composable matrix-operation building blocks, while CuTe provides abstractions for shapes, strides and layout composition used in tiled algorithms. An operation atom describes a small supported operation; larger tiles organize repeated work and data movement. Epilogues transform accumulated results, often adding scale, bias or activation. Templates encode choices at compile time, but they do not absolve the programmer from understanding coordinates, alignment, resource costs and architecture support. Pin dependencies and begin with a prepared supported example. A novel tile DSL is an elective comparison, not a universal prerequisite for basic CUDA.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-058_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-058_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A 2-by-3 logical tile with strides (3,1) maps coordinate (1,2) to offset five. A transposed view uses shape (3,2) and strides (1,3), mapping (2,1) to the same offset. Trace tiny layouts before interpreting a large template type.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
assert 1 * 3 + 2 == 5
assert 2 * 1 + 1 * 3 == 5
values = [-2, 1, 4]
correct = [max(0, x + 1) for x in values]
wrong = [max(0, x) + 1 for x in values]
assert correct == [0, 2, 5] and wrong == [1, 2, 5]
print({"correct_epilogue": correct, "changed_operation_order": wrong})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'correct_epilogue': [0, 2, 5], 'changed_operation_order': [1, 2, 5]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

An epilogue applies bias then ReLU to accumulated values \([-2,1,4]\) with bias one, producing \([0,2,5]\). Moving the bias after ReLU would produce \([1,2,5]\), changing semantics. A fused epilogue must match the reference order, type conversion and scaling contract.

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

Compute offset (1,1) under shape (2,3), strides (3,1).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A template instantiation compiles but fails on the target device. What is missing?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How should a non-tile-aligned matrix be handled?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

When would you choose a library epilogue over a custom kernel?

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a template library removes the need to understand layout or architecture support. , .**

For the concrete failure exercise, a template instantiation compiles but fails on the target device. What is missing?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-058_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUTLASS](https://docs.nvidia.com/cutlass/latest/overview.html)
- [CUDA Tile chapter](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-tile-kernels.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-058: CUTLASS, CuTe and tile abstractions.
Read courses/cuda/cpp/guides/cuda-058.md and courses/cuda/cpp/lessons/cuda-058.md.
Direct prerequisites: `cuda-019`, `cuda-046`, `cuda-053`, `cuda-056`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-058_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-058_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
