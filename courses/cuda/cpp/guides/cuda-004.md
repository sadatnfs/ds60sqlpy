# cuda-004: Parallel decomposition before launch syntax

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-001`, `cuda-002`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Parallel decomposition before launch syntax* with the concrete cases below. Finish with this evidence:
a decomposition that covers every element once and states synchronization requirements. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Decomposition assigns parts of a problem to workers while preserving its mathematical meaning. A map transforms each input independently. A reduction combines many values into one. A scan produces every prefix, so its outputs encode more information than a reduction. Gather reads from chosen locations; scatter writes to chosen locations and needs a conflict policy when destinations overlap. Work counts all operations, while dependency depth counts the longest chain that cannot be parallelized. A useful decomposition names each output owner, describes required inputs and states when producers must finish before consumers read.

## Mathematical contract

\[
\operatorname{exclusive}(x)_i=\sum_{j=0}^{i-1}x_j
\]

The empty prefix at index zero has sum zero. This definition specifies semantics independently of the parallel scan algorithm.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-004_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-004_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Partition 10 elements into conceptual blocks of four. The ownership ranges are [0,4), [4,8) and [8,10). The half-open notation includes the start and excludes the end. Each element appears once; the final block has a tail. Allocating three full blocks of output without a bounds predicate would incorrectly expose positions 10 and 11.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [2, 1, 3, 4]
prefix, total = [], 0
for value in values:
    prefix.append(total)
    total += value
assert prefix == [0, 2, 3, 6] and total == 10
ranges = [list(range(start, min(start + 4, 10))) for start in range(0, 10, 4)]
assert sum(ranges, []) == list(range(10))
print({"exclusive_scan": prefix, "reduction": total, "ownership": ranges})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'exclusive_scan': [0, 2, 3, 6], 'reduction': 10, 'ownership': [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For \([2,1,3,4]\), reduction returns 10. Inclusive scan returns \([2,3,6,10]\), and exclusive scan returns \([0,2,3,6]\). A reduction alone cannot tell element 2 where to write in a stable filtered output. That position comes from a prefix count of earlier selected elements.

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

Tile a width-7, height-3 image with conceptual 4-by-2 tiles.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Two scatter workers both write output\([2]\). Explain why unique input indices are insufficient.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Give the reduction and scan of an empty vector under integer addition.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose map, reduce or scan for allocating stable filtered output positions.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **an evenly divisible toy size proves the indexing scheme works generally.**

For the concrete failure exercise, two scatter workers both write output\([2]\). Explain why unique input indices are insufficient.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-004_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-004: Parallel decomposition before launch syntax.
Read courses/cuda/cpp/guides/cuda-004.md and courses/cuda/cpp/lessons/cuda-004.md.
Direct prerequisites: `cuda-001`, `cuda-002`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-004_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-004_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
