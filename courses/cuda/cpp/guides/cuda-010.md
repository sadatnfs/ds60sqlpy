# cuda-010: Resource ownership and failure-safe cleanup

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-009`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Resource ownership and failure-safe cleanup* with the concrete cases below. Finish with this evidence:
no double release, no leaked first allocation, and clear owner/borrower relationships. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

RAII connects resource lifetime to an owning C++ object's lifetime. Its constructor establishes an invariant, and its destructor releases the resource. Copying a unique owner is usually forbidden; moving transfers ownership and leaves the source empty. This is important for CUDA allocations, streams and events because a copied raw handle does not represent an independent resource. A destructor should not throw during stack unwinding. Error reporting for explicit completion and release should happen in a deliberate path, while final cleanup remains a last safeguard. Asynchronous use adds a further obligation: do not destroy the owner while a queued operation still borrows the resource.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-010_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-010_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

An operation acquires buffer A, then fails to acquire B. If A already belongs to an automatic owner, stack unwinding releases A. The event trace is acquire-A, acquire-B-failed, release-A. If A is only a raw pointer and cleanup exists only at the normal return, the failure path leaks A.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
events = []
try:
    events.append("acquire-A")
    try:
        events.append("acquire-B-failed")
        raise RuntimeError("synthetic allocation failure")
    finally:
        events.append("release-A")
except RuntimeError:
    pass
assert events == ["acquire-A", "acquire-B-failed", "release-A"]
print(events)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
['acquire-A', 'acquire-B-failed', 'release-A']
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Moving owner A into owner B changes who releases the allocation. The moved-from A stores an empty handle; only B releases the original resource. A default copy that leaves two nonempty owners would lead to two releases. Neither a destructor nor a smart-sounding class name alone proves this invariant.

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

Write the ownership invariant for a device-buffer wrapper.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A destructor throws while handling an earlier allocation exception. Why is this dangerous?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an empty owner release?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Extend ownership to two streams borrowing one buffer.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **adding a destructor alone guarantees correctness when copies are still allowed.**

For the concrete failure exercise, a destructor throws while handling an earlier allocation exception. Why is this dangerous?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-010_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-010: Resource ownership and failure-safe cleanup.
Read courses/cuda/cpp/guides/cuda-010.md and courses/cuda/cpp/lessons/cuda-010.md.
Direct prerequisites: `cuda-009`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-010_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-010_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
