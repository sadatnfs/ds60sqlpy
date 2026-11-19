# cuda-037: Divergence, irregular work and algorithm choice

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-021`, `cuda-027`, `cuda-033`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Divergence, irregular work and algorithm choice* with the concrete cases below. Finish with this evidence:
a correctness-preserving strategy and end-to-end evidence that includes sorting or compaction when used. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Divergence occurs when lanes in a warp follow different control-flow paths. It can reduce useful parallel execution, but branches that are uniform across a warp or skip substantial work can be beneficial. Irregular workloads also suffer from imbalance when some lanes have much longer loops. Reordering or compacting work can improve grouping at the cost of an extra pass and changed order. Preserve semantic ordering where required and include preprocessing in end-to-end measurement. Branch elimination that evaluates both expensive sides can make the program slower even when it reduces control flow.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-037_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-037_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Four conceptual lanes process workloads \([1,1,1,9]\). A simplified lockstep cost is nine rounds, with 12 useful lane-rounds out of 36 available positions, or one third utilization. This is a pedagogical model, not an actual CUDA timing prediction.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
workloads = [1, 1, 1, 9]
utilization = sum(workloads) / (len(workloads) * max(workloads))
assert utilization == 1 / 3
assert sum([3, 3, 3, 3]) == sum(workloads)
print({"synthetic_lockstep_useful_fraction": utilization, "preprocess_ms_minus_saved_ms": 2 - 1})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'synthetic_lockstep_useful_fraction': 0.3333333333333333, 'preprocess_ms_minus_saved_ms': 1}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A threshold operation has cheap and expensive categories. Grouping expensive items can make work more uniform, but a 2 ms compaction pass is not worthwhile if it saves only 1 ms of kernel time for a one-shot request. Reuse across many iterations can change that decision.

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

Compute the same simplified utilization for \([3,3,3,3]\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is replacing every branch with both computations risky?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if all predicates are false?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design bucketing for ragged row lengths.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **branches are forbidden on GPUs, or removing every branch necessarily improves execution.**

For the concrete failure exercise, why is replacing every branch with both computations risky?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-037_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
