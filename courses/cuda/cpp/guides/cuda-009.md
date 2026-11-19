# cuda-009: C++ essentials specifically needed at the GPU boundary

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *C++ essentials specifically needed at the GPU boundary* with the concrete cases below. Finish with this evidence:
CPU reference tests and a lifetime explanation. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A pointer identifies storage; a size defines the range your function may use. Pair them explicitly. A const input pointer prevents writes through that pointer, but it does not establish unique ownership or guarantee that another alias cannot modify storage. A vector owns contiguous elements and can lend its data pointer while it remains alive and does not reallocate. A device function cannot generally use an ordinary host vector object because its implementation, allocator and storage belong to the host environment. Use plain element buffers and explicit shape metadata at the boundary, with deliberate integer-width choices for address arithmetic.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-009_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-009_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A CPU affine transform accepts input, output, count, scale and bias. For input \([-1,0,2]\), scale 3 and bias 1, the result is \([-2,1,7]\). Reject mismatched ranges before indexing. If input and output overlap, either document in-place safety or reject that case; const alone does not answer it.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [-1, 0, 2]
result = [3 * value + 1 for value in values]
assert result == [-2, 1, 7]
padded = [1, 2, 99, 3, 4, 99]
row_sums = [sum(padded[r * 3 : r * 3 + 2]) for r in range(2)]
assert row_sums == [3, 7]
print({"affine": result, "row_sums": row_sums})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'affine': [-2, 1, 7], 'row_sums': [3, 7]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A function returning `vector<float>{1,2,3}.data()` returns a pointer to storage whose owner is destroyed at the end of the expression. The pointer value may still print, but dereferencing it is invalid. Return the owning vector, or pass caller-owned storage into the function. Keeping a numeric address does not keep an allocation alive.

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

Describe a row-sum function's minimum buffer metadata for padded storage.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A vector grows after its data pointer was saved. What must be checked?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How should count zero be handled?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Why should a host pointer not be reinterpreted as a device allocation?

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **copying a pointer copies the data, or a host container can be passed to device code unchanged.**

For the concrete failure exercise, a vector grows after its data pointer was saved. What must be checked?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-009_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-009: C++ essentials specifically needed at the GPU boundary.
Read courses/cuda/cpp/guides/cuda-009.md and courses/cuda/cpp/lessons/cuda-009.md.
Direct prerequisites: `cuda-005`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-009_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-009_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
