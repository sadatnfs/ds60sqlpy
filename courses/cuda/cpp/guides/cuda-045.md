# cuda-045: CCCL, Thrust and CUB before writing everything by hand

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-020`, `cuda-021`, `cuda-022`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Compare a Thrust or CUB primitive against a handwritten kernel and justify the library or custom choice.

Work through *CCCL, Thrust and CUB before writing everything by hand* with the concrete cases below. Finish with this evidence:
equivalent semantics, stated temporary-memory needs and a justified library/custom decision. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

CUDA Core Compute Libraries bring maintained building blocks such as Thrust algorithms, CUB primitives and CUDA-oriented standard-library facilities. Their abstractions do not remove ownership, stream or temporary-storage obligations. Prefer a tested library primitive when it matches semantics, and keep a handwritten version as a learning baseline or for a demonstrated special requirement. Some primitive interfaces separate workspace-size queries from execution; read the pinned interface rather than guessing. Iterator adapters can avoid materializing intermediate arrays, but they must preserve valid lifetimes and access patterns.

### Key terms

- **Thrust:** A C++ template library of parallel algorithms, such as sort and reduce, over host and device containers.
- **CUB:** A CUDA library of block-level, warp-level and device-wide primitives with explicit temporary storage.
- **Temporary storage query:** A first CUB call with a null workspace pointer that returns the number of bytes the algorithm needs.
- **Execution policy:** An argument such as `thrust::cuda::par.on(stream)` that selects where and on which stream a Thrust algorithm runs.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-045_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-045_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Transform \([1,2,3,4]\) by squaring and sum, obtaining 30. A fused transform-reduce can avoid a separate \([1,4,9,16]\) allocation when its interface supports the desired operation. The mathematical result is the same; the memory and scheduling behavior differ.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [1, 2, 3, 4]
assert sum(x * x for x in values) == 30
selected = [x for x in [5, 2, 5, 1] if x >= 5]
assert selected == [5, 5]
print({"transform_reduce_reference": 30, "stable_selection": selected})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'transform_reduce_reference': 30, 'stable_selection': [5, 5]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Stable filtering \([5,2,5,1]\) for values at least five returns \([5,5]\). Sorting before filtering also retains the two fives here, but generally changes order. Choose the algorithm according to semantic requirements, not merely the nearest familiar function name.

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

Compare reduce and transform-reduce for sum of squares.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why must a library stream argument be deliberate?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What is the empty sum-of-squares identity?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

State when a custom reduction is justified.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **library calls remove the need to understand allocation, synchronization or data layout.  should be replaced by the pinned release's docs at implementation time.**

For the concrete failure exercise, why must a library stream argument be deliberate?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-045_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Core Compute Libraries](https://nvidia.github.io/cccl/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-045: CCCL, Thrust and CUB before writing everything by hand.
Read courses/cuda/cpp/guides/cuda-045.md and courses/cuda/cpp/lessons/cuda-045.md.
Direct prerequisites: `cuda-020`, `cuda-021`, `cuda-022`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-045_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-045_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
