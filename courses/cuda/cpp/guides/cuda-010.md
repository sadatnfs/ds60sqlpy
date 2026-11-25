# cuda-010: Resource ownership and failure-safe cleanup

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-009`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a move-only buffer owner that never double releases and never leaks a partially initialized allocation.

**Scope:** Allocation ownership, move-only handles, destructors, exception boundaries and status-returning APIs.

**Evidence to produce:** No double release, no leaked first allocation, and clear owner/borrower relationships.

## Purpose, vocabulary and mental model

RAII connects resource lifetime to an owning C++ object's lifetime. Its constructor establishes an invariant, and its destructor releases the resource. Copying a unique owner is usually forbidden; moving transfers ownership and leaves the source empty. This is important for CUDA allocations, streams and events because a copied raw handle does not represent an independent resource. A destructor should not throw during stack unwinding. Error reporting for explicit completion and release should happen in a deliberate path, while final cleanup remains a last safeguard. Asynchronous use adds a further obligation: do not destroy the owner while a queued operation still borrows the resource.

### Key terms

- **Move-only type:** A class whose copy operations are deleted, so ownership can be transferred but never duplicated.
- **Destructor:** A member function that runs when an object's lifetime ends and releases the resource the object owns.
- **Borrower:** Code that uses a resource through a pointer or reference without owning it or controlling its release.
- **Stack unwinding:** The destruction of local objects in reverse order while an exception propagates out of a scope.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-010_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-010_cpu.py
```

## Worked example 1: trace the mechanism

An operation acquires buffer A, then fails to acquire B. If A already belongs to an automatic owner, stack unwinding releases A. The event trace is acquire-A, acquire-B-failed, release-A. If A is only a raw pointer and cleanup exists only at the normal return, the failure path leaks A.

**Why:** An automatic owner's destructor runs during unwinding, so release does not depend on the normal return path.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
['acquire-A', 'acquire-B-failed', 'release-A']
```

**Check:** The reference asserts events == ['acquire-A', 'acquire-B-failed', 'release-A'].

## Worked example 2: change a meaningful condition

Moving owner A into owner B changes who releases the allocation. The moved-from A stores an empty handle; only B releases the original resource. A default copy that leaves two nonempty owners would lead to two releases. Neither a destructor nor a smart-sounding class name alone proves this invariant.

**Why:** Moving transfers the single ownership, so exactly one release happens for one allocation.

**Check:** Delete the copy constructor and verify a copy attempt fails to compile while a move succeeds.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Trace the events: A is acquired, B fails, unwinding runs A's cleanup.

**Trap to avoid:** Freeing A only at the end of the function skips that line when B throws, leaking A.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Move A into B, record that A now holds an empty handle, and release only through B.

**Trap to avoid:** A default member-wise copy duplicates the raw handle, and both destructors free the same memory.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Write the ownership invariant for a device-buffer wrapper.

**Trap to avoid:** Writing only 'the destructor frees memory' omits moves and outstanding GPU work.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A destructor throws while handling an earlier allocation exception. Why is this dangerous?

**Trap to avoid:** Throwing from the destructor to surface a free failure turns one error into an abort.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an empty owner release?

**Trap to avoid:** Calling free on a stale handle in a moved-from owner releases memory now owned by someone else.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Extend ownership to two streams borrowing one buffer.

**Trap to avoid:** Freeing when the host wrapper goes out of scope can release memory a queued kernel still reads.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Adding a destructor alone guarantees correctness when copies are still allowed.** A destructor releases what its owner holds, but an allowed copy creates two owners of one handle. Worked example 2 shows that a default copy leads to two releases of the same allocation. Ownership needs copying disabled and moves that leave the source empty. Worked example 1 adds the failure path: an automatic owner releases A when acquiring B fails, while a raw pointer leaks it.

## Self-check, retrieval and transfer

1. What should a moved-from device buffer owner hold?
2. In worked example 1, what releases buffer A when acquiring B fails?
3. Why should a destructor report errors rather than throw?

Short answers are in the [separate explanations](../solutions/cuda-010_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
