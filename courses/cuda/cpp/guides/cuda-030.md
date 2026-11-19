# cuda-030: Debugging difficult failures without harming the session

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-025`, `cuda-026`, `cuda-028`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Debugging difficult failures without harming the session* with the concrete cases below. Finish with this evidence:
a repair with a regression case and preserved learner source/results. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A minimal reproducer removes unrelated work while preserving the failure. For a shape-dependent bug, reduce dimensions and data complexity independently, then retain the smallest case that still fails. Add source line information and stage-specific checks before interpreting a large trace. Debug builds change optimization and resource usage; a disappearing failure is a clue, not proof of a fix. A device fault can make further operations in a context unreliable. Preserve source and diagnostics before restarting a process. Device reset and shared-engine recovery belong to the resource owner, not an automatic learner-code repair path.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-030_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-030_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A hypothetical bad predicate i<=n fails at lengths 1,33 and 1,001. Reduce it to length one, where index one is already invalid. This gives a tiny regression fixture and a direct explanation. A giant dataset is unnecessary to show the underlying off-by-one error.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
def invalid_indices(n):
    return [i for i in range(n + 1) if not 0 <= i < n]


assert invalid_indices(1) == [1]
assert invalid_indices(33) == [33]
receipt = {"submitted": True, "completed": False, "validated": False}
assert not receipt["validated"]
print({"minimal_bounds_case": invalid_indices(1), "timeout_receipt": receipt})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'minimal_bounds_case': [1], 'timeout_receipt': {'submitted': True, 'completed': False, 'validated': False}}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A recorded timeout contains 'kernel submitted; completion not observed'. It does not contain a correct numerical result. Classify it as incomplete execution and inspect boundedness/dependencies. Do not add an arbitrary sleep and call the change a synchronization fix.

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

List the smallest fields to retain before restarting a failed worker.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is deleting every Docker volume a bad debugging step?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if the minimal case stops reproducing?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a regression test for a tail-only bug.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **adding arbitrary sleeps fixes synchronization or resetting a shared GPU is an acceptable first diagnostic action.**

For the concrete failure exercise, why is deleting every Docker volume a bad debugging step?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-030_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-030: Debugging difficult failures without harming the session.
Read courses/cuda/cpp/guides/cuda-030.md and courses/cuda/cpp/lessons/cuda-030.md.
Direct prerequisites: `cuda-025`, `cuda-026`, `cuda-028`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-030_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-030_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
