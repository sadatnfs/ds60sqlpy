# cuda-037: Divergence, irregular work and algorithm choice

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-021`, `cuda-027`, `cuda-033`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Compare a divergence-reducing strategy against the baseline with end-to-end evidence that includes sorting or compaction.

**Scope:** Divergent paths within warps, variable work lengths, predication, data ordering and compaction overhead.

**Evidence to produce:** A correctness-preserving strategy and end-to-end evidence that includes sorting or compaction when used.

## Purpose, vocabulary and mental model

Divergence occurs when lanes in a warp follow different control-flow paths. It can reduce useful parallel execution, but branches that are uniform across a warp or skip substantial work can be beneficial. Irregular workloads also suffer from imbalance when some lanes have much longer loops. Reordering or compacting work can improve grouping at the cost of an extra pass and changed order. Preserve semantic ordering where required and include preprocessing in end-to-end measurement. Branch elimination that evaluates both expensive sides can make the program slower even when it reduces control flow.

### Key terms

- **Warp divergence:** Lanes of one warp taking different branch paths, so the paths execute one after another with lanes masked.
- **Load imbalance:** Uneven work per thread or block that leaves some hardware idle while the slowest work finishes.
- **Warp-uniform branch:** A branch whose condition has the same value for every lane of a warp, so it causes no divergence.
- **Work reordering:** Sorting or grouping items so lanes with similar paths or costs run together, at the price of the reorder step.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-037_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-037_cpu.py
```

## Worked example 1: trace the mechanism

Four conceptual lanes process workloads \([1,1,1,9]\). A simplified lockstep cost is nine rounds, with 12 useful lane-rounds out of 36 available positions, or one third utilization. This is a pedagogical model, not an actual CUDA timing prediction.

**Why:** Lanes with workload 1 idle for 8 rounds while one lane continues, so only 12 of 36 slots do work.

```python
workloads = [1, 1, 1, 9]
utilization = sum(workloads) / (len(workloads) * max(workloads))
assert utilization == 1 / 3
assert sum([3, 3, 3, 3]) == sum(workloads)
print({"synthetic_lockstep_useful_fraction": utilization, "preprocess_ms_minus_saved_ms": 2 - 1})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'synthetic_lockstep_useful_fraction': 0.3333333333333333, 'preprocess_ms_minus_saved_ms': 1}
```

**Check:** The reference asserts utilization == 1 / 3 and labels the value synthetic, not a timing.

## Worked example 2: change a meaningful condition

A threshold operation has cheap and expensive categories. Grouping expensive items can make work more uniform, but a 2 ms compaction pass is not worthwhile if it saves only 1 ms of kernel time for a one-shot request. Reuse across many iterations can change that decision.

**Why:** Net cost rises by 1 ms, so grouping only pays if the grouped data is reused across runs.

**Check:** The reference prints preprocess_ms_minus_saved_ms 1; measure end-to-end time before deciding.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Take the longest workload 9 as rounds, sum useful work 12, and divide by 4 lanes times 9 rounds.

**Trap to avoid:** Averaging the workloads to 3 and assuming 3 rounds ignores that lockstep waits for the slowest lane.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Compare 2 ms of compaction with 1 ms of kernel savings for a one-shot request.

**Trap to avoid:** Adopting bucketing because it made the kernel faster ignores the preprocessing cost.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute the same simplified utilization for \([3,3,3,3]\).

**Trap to avoid:** Reasoning that equal total work means equal utilization misses that balance matters.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is replacing every branch with both computations risky?

**Trap to avoid:** Rewriting every if as a select to remove divergence can create invalid operations.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if all predicates are false?

**Trap to avoid:** A branch-free version that still loads or writes for every lane does unnecessary memory traffic.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design bucketing for ragged row lengths.

**Trap to avoid:** Bucketing without saving original indices returns correct rows in the wrong order.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Branches are forbidden on GPUs, or removing every branch necessarily improves execution.** Branches are allowed and often useful: a warp-uniform branch costs little, and a branch that skips expensive work saves time. Removing branches by computing both sides doubles work and can raise errors on the unused side. Worked example 2 also shows that regrouping divergent work costs a compaction pass, which pays off only when the saved kernel time exceeds it or the grouping is reused.

## Self-check, retrieval and transfer

1. What utilization does the lockstep model give for workloads [2,2,2,8]?
2. When is a branch warp-uniform?
3. Why might reordering work change results?

Short answers are in the [separate explanations](../solutions/cuda-037_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-037: Divergence, irregular work and algorithm choice.
Read courses/cuda/cpp/guides/cuda-037.md and courses/cuda/cpp/lessons/cuda-037.md.
Direct prerequisites: `cuda-021`, `cuda-027`, `cuda-033`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-037_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-037_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
