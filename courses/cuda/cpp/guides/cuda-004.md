# cuda-004: Parallel decomposition before launch syntax

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-001`, `cuda-002`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Design a decomposition that covers every element exactly once and states each synchronization requirement.

**Scope:** Domain decomposition, task decomposition, work, dependency depth, granularity, load balance and boundary work.

**Evidence to produce:** A decomposition that covers every element once and states synchronization requirements.

## Purpose, vocabulary and mental model

Decomposition assigns parts of a problem to workers while preserving its mathematical meaning. A map transforms each input independently. A reduction combines many values into one. A scan produces every prefix, so its outputs encode more information than a reduction. Gather reads from chosen locations; scatter writes to chosen locations and needs a conflict policy when destinations overlap. Work counts all operations, while dependency depth counts the longest chain that cannot be parallelized. A useful decomposition names each output owner, describes required inputs and states when producers must finish before consumers read.

### Key terms

- **Map:** A pattern in which each output is computed independently from its own input element.
- **Reduction:** A pattern that combines many values into one result with an associative operation such as addition or maximum.
- **Scan:** A pattern that produces every prefix combination of its input, so output i depends on all earlier inputs.
- **Dependency depth:** The length of the longest chain of operations that must run in sequence, which bounds parallel speedup.
- **Scatter:** A pattern that writes to computed destinations and needs a conflict policy when destinations overlap.

## Mathematical contract

\[
\operatorname{exclusive}(x)_i=\sum_{j=0}^{i-1}x_j
\]

The empty prefix at index zero has sum zero. This definition specifies semantics independently of the parallel scan algorithm.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-004_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-004_cpu.py
```

## Worked example 1: trace the mechanism

Partition 10 elements into conceptual blocks of four. The ownership ranges are [0,4), [4,8) and [8,10). The half-open notation includes the start and excludes the end. Each element appears once; the final block has a tail. Allocating three full blocks of output without a bounds predicate would incorrectly expose positions 10 and 11.

**Why:** Half-open ranges [0,4), [4,8) and [8,10) cover every index exactly once, and the final range stops at 10.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'exclusive_scan': [0, 2, 3, 6], 'reduction': 10, 'ownership': [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]}
```

**Check:** The reference concatenates the ranges and asserts they equal list(range(10)), catching both gaps and overruns.

## Worked example 2: change a meaningful condition

For \([2,1,3,4]\), reduction returns 10. Inclusive scan returns \([2,3,6,10]\), and exclusive scan returns \([0,2,3,6]\). A reduction alone cannot tell element 2 where to write in a stable filtered output. That position comes from a prefix count of earlier selected elements.

**Why:** The exclusive scan records the sum before each element, so element i learns how many units precede it.

**Check:** The reference asserts prefix == [0, 2, 3, 6] and total == 10; add the last prefix and last value to get 10.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Step through starts 0, 4 and 8 with block size 4, clamp each end to 10, and list the half-open ranges.

**Trap to avoid:** Writing ranges as [0,3], [4,7], [8,11] without clamping invents positions 10 and 11, outside the output.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Compute the total once, then build inclusive and exclusive scans of [2, 1, 3, 4] by carrying a running sum.

**Trap to avoid:** Using the reduction value 10 to place selected elements fails because every element receives the same number.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Tile a width-7, height-3 image with conceptual 4-by-2 tiles.

**Trap to avoid:** Checking only x < 7 lets the bottom tile write row 3, which does not exist in a height-3 image.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Two scatter workers both write output\([2]\). Explain why unique input indices are insufficient.

**Trap to avoid:** Accepting plain stores and assuming the last writer wins produces a nondeterministic value when both writes race.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Give the reduction and scan of an empty vector under integer addition.

**Trap to avoid:** Returning [0] for the exclusive scan adds an element that no input owns and breaks length equality.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose map, reduce or scan for allocating stable filtered output positions.

**Trap to avoid:** Assigning destinations with an atomic counter gives unique slots but scrambles the order across threads.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **An evenly divisible toy size proves the indexing scheme works generally.** Divisible sizes hide tail and boundary handling. Worked example 1 partitions 10 elements into blocks of four and leaves a final range of [8,10); an indexing scheme tested only at 8 or 12 never exercises that tail, so out-of-range writes or skipped elements stay invisible.

## Self-check, retrieval and transfer

1. Write the ownership ranges for 13 elements in blocks of five.
2. Why does a stable filter need a scan rather than a reduction?
3. What extra rule does scatter need that map does not?

Short answers are in the [separate explanations](../solutions/cuda-004_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
