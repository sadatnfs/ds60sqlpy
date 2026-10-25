# cuda-004: Parallel decomposition before launch syntax

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-001`, `cuda-002`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain parallel decomposition before launch syntax using the concrete cases below. Produce a decomposition that covers every element once and states synchronization requirements.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

Decomposition assigns parts of a problem to workers while preserving its mathematical meaning. A map transforms each input independently. A reduction combines many values into one. A scan produces every prefix, so its outputs encode more information than a reduction. Gather reads from chosen locations; scatter writes to chosen locations and needs a conflict policy when destinations overlap. Work counts all operations, while dependency depth counts the longest chain that cannot be parallelized. A useful decomposition names each output owner, describes required inputs and states when producers must finish before consumers read.

## Mathematical contract

\[
\operatorname{exclusive}(x)_i=\sum_{j=0}^{i-1}x_j
\]

The empty prefix at index zero has sum zero. This definition specifies semantics independently of the parallel scan algorithm.

## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/cuda-004_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-004_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For \([2,1,3,4]\), reduction returns 10. Inclusive scan returns \([2,3,6,10]\), and exclusive scan returns \([0,2,3,6]\). A reduction alone cannot tell element 2 where to write in a stable filtered output. That position comes from a prefix count of earlier selected elements.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Start with the literal input and intermediate quantities in worked example 1.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Identify exactly which condition changes in worked example 2.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 3

Tile a width-7, height-3 image with conceptual 4-by-2 tiles.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

Two scatter workers both write output\([2]\). Explain why unique input indices are insufficient.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

Give the reduction and scan of an empty vector under integer addition.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Choose map, reduce or scan for allocating stable filtered output positions.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **an evenly divisible toy size proves the indexing scheme works generally.**

For the concrete failure exercise, two scatter workers both write output\([2]\). Explain why unique input indices are insufficient.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-004_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
