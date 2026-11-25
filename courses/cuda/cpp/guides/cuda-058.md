# cuda-058: CUTLASS, CuTe and tile abstractions

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-019`, `cuda-046`, `cuda-053`, `cuda-056`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Configure a CUTLASS or CuTe kernel with correct layouts and benchmark it against a library baseline.

**Scope:** Layout composition, tile shapes, operation atoms, epilogues and policy choices.

**Evidence to produce:** Correct layouts, supported feature declaration and benchmark against an appropriate library baseline.

## Purpose, vocabulary and mental model

CUTLASS supplies composable matrix-operation building blocks, while CuTe provides abstractions for shapes, strides and layout composition used in tiled algorithms. An operation atom describes a small supported operation; larger tiles organize repeated work and data movement. Epilogues transform accumulated results, often adding scale, bias or activation. Templates encode choices at compile time, but they do not absolve the programmer from understanding coordinates, alignment, resource costs and architecture support. Pin dependencies and begin with a prepared supported example. A novel tile DSL is an elective comparison, not a universal prerequisite for basic CUDA.

### Key terms

- **CUTLASS:** An NVIDIA C++ template library for building high-performance matrix multiply and related kernels.
- **CuTe layout:** A pair of shape and stride that maps logical coordinates to memory offsets in CUTLASS 3.
- **Epilogue:** The final stage of a GEMM kernel that applies scaling, bias or activation before storing results.
- **MMA atom:** The smallest matrix-multiply-accumulate instruction shape that CuTe composes into larger tiles.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-058_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-058_cpu.py
```

## Worked example 1: trace the mechanism

A 2-by-3 logical tile with strides (3,1) maps coordinate (1,2) to offset five. A transposed view uses shape (3,2) and strides (1,3), mapping (2,1) to the same offset. Trace tiny layouts before interpreting a large template type.

**Why:** Coordinate (1, 2) gives 3 + 2 = 5, and the transposed (2, 1) gives 2 + 3 = 5, so both name the same element.

```python
assert 1 * 3 + 2 == 5
assert 2 * 1 + 1 * 3 == 5
values = [-2, 1, 4]
correct = [max(0, x + 1) for x in values]
wrong = [max(0, x) + 1 for x in values]
assert correct == [0, 2, 5] and wrong == [1, 2, 5]
print({"correct_epilogue": correct, "changed_operation_order": wrong})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'correct_epilogue': [0, 2, 5], 'changed_operation_order': [1, 2, 5]}
```

**Check:** The reference asserts 1 * 3 + 2 == 5 and 2 * 1 + 1 * 3 == 5.

## Worked example 2: change a meaningful condition

An epilogue applies bias then ReLU to accumulated values \([-2,1,4]\) with bias one, producing \([0,2,5]\). Moving the bias after ReLU would produce \([1,2,5]\), changing semantics. A fused epilogue must match the reference order, type conversion and scaling contract.

**Why:** ReLU gives [0, 2, 5], matching the reference order of operations.

**Check:** The reference asserts correct == [0, 2, 5] and wrong == [1, 2, 5].

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Compute offset as row times stride 3 plus column times stride 1 for the 2-by-3 tile, then apply the transposed view's strides (1, 3).

**Trap to avoid:** Swapping shape without swapping strides makes the transposed view index the wrong memory entirely.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Add bias 1 to accumulators [-2, 1, 4] for [-1, 2, 5], then apply ReLU.

**Trap to avoid:** Applying ReLU first and adding bias afterward gives [1, 2, 5], which changes the first element.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute offset (1,1) under shape (2,3), strides (3,1).

**Trap to avoid:** Using shape (2, 3) as strides gives 1 * 2 + 1 * 3 = 5, the wrong element.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A template instantiation compiles but fails on the target device. What is missing?

**Trap to avoid:** Treating a clean compile as proof of support ignores runtime dispatch requirements.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How should a non-tile-aligned matrix be handled?

**Trap to avoid:** Assuming the padding is zero adds garbage into partial tiles.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

When would you choose a library epilogue over a custom kernel?

**Trap to avoid:** Writing a custom kernel before checking the library duplicates tested work.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A template library removes the need to understand layout or architecture support.** Templates encode tile and layout choices but do not check that they match your data or device. A wrong stride compiles and silently computes the wrong offsets, and an instantiation can target instructions the device lacks. Trace a tiny layout by hand, as worked example 1 does, and confirm architecture support.

## Self-check, retrieval and transfer

1. What offset does (1,1) map to under shape (2,3) and strides (3,1)?
2. What does worked example 2 produce when bias comes after ReLU?
3. An instantiation compiles but fails on the device. What is missing?

Short answers are in the [separate explanations](../solutions/cuda-058_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
