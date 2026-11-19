# cuda-016: GPU memory spaces in one working program

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-013`, `cuda-015`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *GPU memory spaces in one working program* with the concrete cases below. Finish with this evidence:
a justified storage choice for each variable and a correct result across two input shapes. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Storage spaces describe accessibility and lifetime as well as likely performance. Global allocations can hold data used by many kernels. Shared memory belongs to a block and lasts for that block's execution. Registers hold thread-local values, but a large local array or register pressure can place values in local memory backed by device memory. Constant storage is useful for certain read-only patterns, especially broadcast-like access, but it is not an automatic speedup for arbitrary divergent addresses. A compiler resource report helps explain implementation choices; source variable scope alone does not prove where every value resides.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-016_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-016_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

In a three-tap filter, the input and output images live in global allocations. A thread's running sum is a scalar candidate for a register. A cooperatively loaded tile belongs in shared memory. Three common coefficients may use read-only or constant storage. These are choices to validate, not declarations that force a faster program.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
bytes_per_thread = 1024 * 4
logical_bytes_per_block = bytes_per_thread * 128
assert bytes_per_thread == 4096 and logical_bytes_per_block == 524288
placements = {"image": "global", "cooperative_tile": "shared", "sum": "thread local"}
print({"logical_temporary_bytes": logical_bytes_per_block, "storage_roles": placements})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'logical_temporary_bytes': 524288, 'storage_roles': {'image': 'global', 'cooperative_tile': 'shared', 'sum': 'thread local'}}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A per-thread temporary array with 1,024 floats needs 4,096 bytes per thread. At 128 threads that is 524,288 bytes of logical temporary data, before other resources. Calling it 'local' does not make it inexpensive. Reduce live working state or choose a different algorithm, then inspect compiler and runtime evidence.

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

Assign storage for a reused image, a block tile and a scalar sum.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

An author says a local array is guaranteed to stay in registers. Correct the claim.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Can one block read another block's ordinary shared array?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Decide whether to use constant storage for a 64-entry lookup table.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **every local variable stays in a register, or shared memory is shared across all blocks.**

For the concrete failure exercise, an author says a local array is guaranteed to stay in registers. Correct the claim.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-016_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-016: GPU memory spaces in one working program.
Read courses/cuda/cpp/guides/cuda-016.md and courses/cuda/cpp/lessons/cuda-016.md.
Direct prerequisites: `cuda-013`, `cuda-015`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-016_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-016_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
