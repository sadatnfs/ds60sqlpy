# cuda-030: Debugging difficult failures without harming the session

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-025`, `cuda-026`, `cuda-028`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Reduce a shape-dependent failure to a minimal reproducer and repair it with a regression case.

**Scope:** Minimal reproductions, deterministic fixtures, launch parameter minimization, line information, debug-build effects and context failure.

**Evidence to produce:** A repair with a regression case and preserved learner source/results.

## Purpose, vocabulary and mental model

A minimal reproducer removes unrelated work while preserving the failure. For a shape-dependent bug, reduce dimensions and data complexity independently, then retain the smallest case that still fails. Add source line information and stage-specific checks before interpreting a large trace. Debug builds change optimization and resource usage; a disappearing failure is a clue, not proof of a fix. A device fault can make further operations in a context unreliable. Preserve source and diagnostics before restarting a process. Device reset and shared-engine recovery belong to the resource owner, not an automatic learner-code repair path.

### Key terms

- **Regression test:** A test that reproduces a fixed defect so the failure cannot silently return.
- **Line information:** Debug metadata, added with the `-lineinfo` option, that maps device instructions to source lines.
- **Device fault:** An error during kernel execution that can leave the CUDA context unusable until the process restarts.
- **Debug build:** A compilation, for example with `-G`, that disables device optimizations and can change timing and resource use.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-030_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-030_cpu.py
```

## Worked example 1: trace the mechanism

A hypothetical bad predicate i<=n fails at lengths 1,33 and 1,001. Reduce it to length one, where index one is already invalid. This gives a tiny regression fixture and a direct explanation. A giant dataset is unnecessary to show the underlying off-by-one error.

**Why:** A length-one array has only index 0, so the bad predicate already fails.

```python
def invalid_indices(n):
    return [i for i in range(n + 1) if not 0 <= i < n]


assert invalid_indices(1) == [1]
assert invalid_indices(33) == [33]
receipt = {"submitted": True, "completed": False, "validated": False}
assert not receipt["validated"]
print({"minimal_bounds_case": invalid_indices(1), "timeout_receipt": receipt})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'minimal_bounds_case': [1], 'timeout_receipt': {'submitted': True, 'completed': False, 'validated': False}}
```

**Check:** The reference asserts invalid_indices(1) == [1] and invalid_indices(33) == [33].

## Worked example 2: change a meaningful condition

A recorded timeout contains 'kernel submitted; completion not observed'. It does not contain a correct numerical result. Classify it as incomplete execution and inspect boundedness/dependencies. Do not add an arbitrary sleep and call the change a synchronization fix.

**Why:** Submitted without observed completion means no result exists to validate.

**Check:** The reference receipt marks completed and validated False; keep that classification.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Shrink the failing inputs to length one, where i <= n reaches index 1.

**Trap to avoid:** Debugging the 1,001-element case first buries one bad index in a large trace.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Classify the record as incomplete execution and inspect loop bounds and waits.

**Trap to avoid:** Adding a sleep before reading output may hide the hang without fixing the dependency.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

List the smallest fields to retain before restarting a failed worker.

**Trap to avoid:** Restarting first and collecting later loses the diagnostics tied to the failure.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is deleting every Docker volume a bad debugging step?

**Trap to avoid:** Wiping everything and seeing a clean start mistakes a reset for a repair.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if the minimal case stops reproducing?

**Trap to avoid:** Declaring a fix because a smaller unrelated case passes ignores the original trigger.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a regression test for a tail-only bug.

**Trap to avoid:** Testing only the divisible size passes while the tail bug remains.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Adding arbitrary sleeps fixes synchronization or resetting a shared GPU is an acceptable first diagnostic action.** A sleep changes timing, which can hide a race without creating any ordering, so the defect returns on a different machine or load. Resetting a shared GPU destroys other users' work and the evidence of your own fault. Worked example 1 shows the better path: shrink the failure to the smallest input, here length one, and turn it into a regression test before changing code. Keep the failing command and its exact error text with the fixture.

## Self-check, retrieval and transfer

1. Why does length one expose the `i <= n` bug in worked example 1?
2. How should a timeout with no completion be classified?
3. What does it mean if a bug disappears in a debug build?

Short answers are in the [separate explanations](../solutions/cuda-030_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
