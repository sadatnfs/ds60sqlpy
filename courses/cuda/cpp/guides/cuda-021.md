# cuda-021: Scans and stream compaction

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-020`, `cuda-004`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement stable stream compaction with exact counts and order for empty, all-match and no-match inputs.

Work through *Scans and stream compaction* with the concrete cases below. Finish with this evidence:
exact output counts and element order for empty, all-match and no-match cases. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

An exclusive scan gives each item the reduction of preceding items; an inclusive scan includes the item itself. For stable compaction, map the selection predicate to zeros and ones, scan those flags, then let selected input i write to its exclusive prefix position. Stability means selected elements keep their relative order. Multiple blocks require scanning block totals and adding offsets in another stage. A total count says how much output is needed but does not assign every destination. Separate input and output or prove that aliasing cannot overwrite unread values.

### Key terms

- **Exclusive scan:** A prefix operation in which output i combines the inputs before position i, starting from the identity.
- **Inclusive scan:** A prefix operation in which output i combines the inputs up to and including position i.
- **Stream compaction:** Copying only selected elements into a dense output, using scanned flags as destination offsets.
- **Stable order:** A guarantee that selected elements keep their original relative order in the output.

## Mathematical contract

\[
p_i=\sum_{j=0}^{i-1}f_j,\qquad N_{\mathrm{out}}=\sum_{j=0}^{n-1}f_j
\]

Each selection flag f is zero or one. A selected element writes at its exclusive prefix p, preserving original order.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-021_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-021_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

For values \([8,3,6,1,4]\), select even values. Flags are \([1,0,1,0,1]\), exclusive positions are \([0,1,1,2,2]\), and selected writes produce \([8,6,4]\). Nonselected elements have positions too, but they do not write.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [8, 3, 6, 1, 4]
flags = [int(v % 2 == 0) for v in values]
positions, count = [], 0
for flag in flags:
    positions.append(count)
    count += flag
out = [None] * count
for v, flag, position in zip(values, flags, positions):
    if flag:
        out[position] = v
assert out == [8, 6, 4] and positions == [0, 1, 1, 2, 2]
print({"flags": flags, "positions": positions, "compacted": out})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'flags': [1, 0, 1, 0, 1], 'positions': [0, 1, 1, 2, 2], 'compacted': [8, 6, 4]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For flags \([0,0,0]\), the exclusive scan is \([0,0,0]\) and count is zero. For \([1,1,1]\), positions are \([0,1,2]\) and count is three. These cases catch allocating from the final exclusive prefix alone without adding the final flag.

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

Compact \([5,2,7,8]\) for values greater than four.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is the last exclusive prefix insufficient for count?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What are scan and compact outputs for empty input?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Use scan to build ragged row offsets from lengths \([2,0,3]\).

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a parallel sum is enough to recover every element's output position.**

For the concrete failure exercise, why is the last exclusive prefix insufficient for count?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-021_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-021: Scans and stream compaction.
Read courses/cuda/cpp/guides/cuda-021.md and courses/cuda/cpp/lessons/cuda-021.md.
Direct prerequisites: `cuda-020`, `cuda-004`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-021_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-021_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
