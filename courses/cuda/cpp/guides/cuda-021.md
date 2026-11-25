# cuda-021: Scans and stream compaction

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-020`, `cuda-004`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement stable stream compaction with exact counts and order for empty, all-match and no-match inputs.

**Scope:** Inclusive versus exclusive prefix sums, local scan and block offsets, work-efficient design, stable compaction and allocation of output positions.

**Evidence to produce:** Exact output counts and element order for empty, all-match and no-match cases.

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

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-021_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-021_cpu.py
```

## Worked example 1: trace the mechanism

For values \([8,3,6,1,4]\), select even values. Flags are \([1,0,1,0,1]\), exclusive positions are \([0,1,1,2,2]\), and selected writes produce \([8,6,4]\). Nonselected elements have positions too, but they do not write.

**Why:** The exclusive prefix at a selected element counts selected elements before it, so 8 lands at slot 0, 6 at slot 1 and 4 at slot 2 in original order.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'flags': [1, 0, 1, 0, 1], 'positions': [0, 1, 1, 2, 2], 'compacted': [8, 6, 4]}
```

**Check:** The CPU reference asserts positions == [0, 1, 1, 2, 2] and out == [8, 6, 4]; on a GPU compare the compacted buffer element by element, not as a set.

## Worked example 2: change a meaningful condition

For flags \([0,0,0]\), the exclusive scan is \([0,0,0]\) and count is zero. For \([1,1,1]\), positions are \([0,1,2]\) and count is three. These cases catch allocating from the final exclusive prefix alone without adding the final flag.

**Why:** For [1, 1, 1] the last exclusive prefix is 2 while three items survive, and for [0, 0, 0] the same formula correctly gives zero.

**Check:** Assert count == 0 for the empty selection and count == 3 for the full one, and place a sentinel after the output to catch a short allocation.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Map each of [8, 3, 6, 1, 4] to an even flag, run an exclusive prefix sum over the flags, then let flagged elements write at their position.

**Trap to avoid:** Letting each thread claim a slot with atomicAdd on a counter also yields three outputs, but their order depends on scheduling and may come back as [6, 8, 4].

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Run the scan on the all-zero and all-one flag arrays and compute count as the final exclusive prefix plus the final flag in both cases.

**Trap to avoid:** Sizing the output from the last exclusive prefix alone allocates two slots for three survivors, and the third write overruns the buffer.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compact \([5,2,7,8]\) for values greater than four.

**Trap to avoid:** Writing every element at its own position lets the rejected 2 overwrite slot 1 before or after 7 depending on thread timing.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is the last exclusive prefix insufficient for count?

**Trap to avoid:** Adding one unconditionally to the last prefix overcounts whenever the final element is rejected, as in [1, 0, 1, 0, 0].

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What are scan and compact outputs for empty input?

**Trap to avoid:** Computing count as positions[n - 1] + flags[n - 1] for n == 0 reads index -1, which in C++ is out of bounds before the buffer.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Use scan to build ragged row offsets from lengths \([2,0,3]\).

**Trap to avoid:** Using an inclusive scan [2, 2, 5] as row starts shifts every row by its own length and makes row 0 begin at 2.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A parallel sum is enough to recover every element's output position.** A sum gives one total, but compaction needs a different position for each selected element: the count of selected elements before it. That is an exclusive scan of the flags, as worked example 1 shows with positions [0,1,1,2,2]. The total count still needs the last prefix plus the last flag.

## Self-check, retrieval and transfer

1. Give the exclusive scan of flags [0,1,1,0,1].
2. What does stability mean for compaction?
3. What extra stage do multiple blocks need for a scan?

Short answers are in the [separate explanations](../solutions/cuda-021_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
