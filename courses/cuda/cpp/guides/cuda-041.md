# cuda-041: Stream-ordered allocation and memory pools

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-010`, `cuda-028`, `cuda-039`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Verify that stream-ordered allocations have no use-after-free and explain retained versus live pool memory.

**Scope:** Allocation/free order, pool reuse, cross-stream lifetime, allocation overhead and memory retained for reuse.

**Evidence to produce:** No use-after-free, correct event ordering and an explained retained-versus-live memory report.

## Purpose, vocabulary and mental model

A stream-ordered allocator treats allocation and free as operations with ordering relationships. It can reuse pooled storage efficiently, but the program must still ensure that every access occurs after allocation and before the relevant free/reuse. Cross-stream consumers require explicit dependencies. Memory returned to a pool can remain reserved for reuse, so reported device memory need not immediately drop to zero. Distinguish live application allocations from reserved pool storage. Pool behavior and support are runtime capabilities, not assumptions justified by a function name in documentation.

### Key terms

- **cudaMallocAsync:** A stream-ordered allocation whose memory becomes usable in stream order and returns to a pool with `cudaFreeAsync`.
- **Memory pool:** A driver-managed reservoir that reuses freed device memory instead of returning it to the system immediately.
- **Release threshold:** A pool attribute that sets how much unused memory the pool may keep reserved.
- **Use-after-free:** Accessing an allocation after it was freed; with `cudaFreeAsync`, any work not ordered before the free must not touch it.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-041_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-041_cpu.py
```

## Worked example 1: trace the mechanism

Stream A allocates X, writes X and records ready. Stream B waits, reads X and records done. Before A frees X, A waits for done. This closes both the producer-to-consumer edge and the consumer-to-reuse edge. The first event alone is insufficient for lifetime safety.

**Why:** Ready guards the read and done guards the free, closing both edges.

```python
events = [
    "allocate_A",
    "write_A",
    "ready",
    "wait_ready_B",
    "read_B",
    "done",
    "wait_done_A",
    "free_A",
]
assert events.index("read_B") < events.index("free_A")
reserved_mib, live_mib = 64, 0
assert reserved_mib >= live_mib
print({"lifetime_order": events, "reserved_MiB": reserved_mib, "live_MiB": live_mib})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'lifetime_order': ['allocate_A', 'write_A', 'ready', 'wait_ready_B', 'read_B', 'done', 'wait_done_A', 'free_A'], 'reserved_MiB': 64, 'live_MiB': 0}
```

**Check:** The reference asserts read_B comes before free_A in the event list.

## Worked example 2: change a meaningful condition

A pool reserves 64 MiB and the application currently uses 16 MiB. After freeing that allocation back to the pool, live usage may be zero while reservation remains 64 MiB. Calling this a leak without examining ownership and retention policy confuses two different measurements.

**Why:** After the free, live is 0 MiB while the pool keeps 64 MiB reserved for reuse.

**Check:** The reference prints reserved_MiB 64 and live_MiB 0; trim the pool and confirm release.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Order allocate, write, ready, wait in B, read, done, wait in A, then free X.

**Trap to avoid:** Using only the ready event lets A free X while B may still be reading.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Report live and reserved bytes separately and check pool retention policy.

**Trap to avoid:** Calling the reserved 64 MiB a leak ignores that the pool intentionally holds it.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Name both event dependencies in the cross-stream example.

**Trap to avoid:** Treating one event as covering both directions leaves the reuse hazard open.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A buffer is freed immediately after enqueuing work in another stream. Diagnose it.

**Trap to avoid:** Synchronizing the freeing stream alone does not wait for the other stream.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should allocation failure preserve?

**Trap to avoid:** Continuing with a null pointer as if allocation succeeded produces invalid output.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a repeated temporary-buffer workload.

**Trap to avoid:** An unbounded pool can grow until other work cannot allocate.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Returning memory to a pool means the GPU's visible memory usage must immediately fall to zero.** A pool keeps freed memory reserved so later allocations are fast, so the device report can stay high while live usage is zero. Worked example 2 shows a 64 MiB reservation with nothing live, which is a retention policy, not a leak. Confirm a leak by tracking live allocations and their owners, and use the release threshold if the reserved memory must return to the system sooner. Report reserved and live bytes separately, since worked example 2 ends with 64 MiB reserved and nothing live.

## Self-check, retrieval and transfer

1. Which two edges make the cross-stream allocation in worked example 1 safe?
2. Why is freeing right after enqueuing work in another stream unsafe?
3. What does a stream-ordered free promise?

Short answers are in the [separate explanations](../solutions/cuda-041_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [Allocator chapter](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/stream-ordered-memory-allocation.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-041: Stream-ordered allocation and memory pools.
Read courses/cuda/cpp/guides/cuda-041.md and courses/cuda/cpp/lessons/cuda-041.md.
Direct prerequisites: `cuda-010`, `cuda-028`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-041_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-041_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
