# cuda-028: Memory ordering and atomic scope

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-022`, `cuda-027`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Explain what each fence, acquire and release operation establishes in a flag publication protocol and what it does not.

**Scope:** Atomicity, visibility, ordering, acquire/release, memory fences and thread/block/device/system scope.

**Evidence to produce:** The learner can explain what each synchronization operation establishes and what it does not.

## Purpose, vocabulary and mental model

Atomicity means one operation is indivisible with respect to competing operations at its scope. Ordering specifies how memory operations relate; visibility concerns which observer can see writes. Publishing a payload through a flag requires a protocol that orders the payload write before a release operation and the consumer's payload read after an appropriate acquire. Both sides must use compatible synchronization and scope. A relaxed atomic counter can correctly count events without publishing unrelated payloads. A fence orders operations but does not force another block to run, so it cannot repair a residency deadlock in an improvised global barrier.

### Key terms

- **Memory fence:** An instruction such as `__threadfence()` that orders a thread's memory operations as observed at a given scope.
- **Release and acquire:** A pairing in which a release store publishes earlier writes and a matching acquire load makes them visible to the reader.
- **Atomic scope:** The set of threads, such as a block, device or system, with respect to which an atomic operation is indivisible.
- **Relaxed atomic:** An atomic operation that is indivisible but imposes no ordering on other memory accesses.
- **Visibility:** Whether a write made by one thread can be observed by another thread.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-028_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-028_cpu.py
```

## Worked example 1: trace the mechanism

A producer writes payload 42, then releases a ready flag. A consumer acquires that publication before reading the payload. The happens-before chain connects payload write to payload read. This is a conceptual protocol; an actual CUDA implementation must use supported atomic types, scope and participating execution conditions.

**Why:** A release store orders earlier writes before the flag, and an acquire load that sees it orders later reads after it.

```python
events = ["payload_write", "release_flag", "acquire_flag", "payload_read"]
positions = {name: i for i, name in enumerate(events)}
assert (
    positions["payload_write"]
    < positions["release_flag"]
    < positions["acquire_flag"]
    < positions["payload_read"]
)
print({"conceptual_happens_before": events, "GPU_memory_model_test": False})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'conceptual_happens_before': ['payload_write', 'release_flag', 'acquire_flag', 'payload_read'], 'GPU_memory_model_test': False}
```

**Check:** The reference asserts the four positions are strictly increasing and prints GPU_memory_model_test False, so a device litmus test is still needed.

## Worked example 2: change a meaningful condition

Two workers atomically increment a count, giving count two, while writing separate payloads without publication ordering. The count's arithmetic can be correct even though the payload protocol is incomplete. 'Atomic' describes the increment, not every access in the surrounding program.

**Why:** atomicAdd gives a correct count of two, but says nothing about when each worker's payload becomes visible.

**Check:** Check that a consumer reading the count before the payloads would be guarded by an acquire on a published flag.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Order four events: write payload 42, release the ready flag, acquire the flag in the consumer, then read the payload.

**Trap to avoid:** Using a plain volatile flag with no release or acquire semantics lets the consumer see ready before 42 is visible.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Separate the atomic counter from the payload protocol and add release and acquire to the publication.

**Trap to avoid:** Reasoning that the atomic increment also publishes the payload confuses arithmetic atomicity with ordering.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Name the four events in the publication chain.

**Trap to avoid:** Listing only write and read assumes program order on one thread carries to another.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why does a memory fence not make a sleeping producer execute?

**Trap to avoid:** Adding more fences in the waiting consumer still never schedules a non-resident producer.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

When might block-scope synchronization be insufficient?

**Trap to avoid:** Using block scope for a host observer leaves the host free to see a stale payload.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Apply the reasoning to a ring buffer slot.

**Trap to avoid:** Indexing slots with head mod capacity but not tracking fullness overwrites unread data on wraparound.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Incrementing an atomic flag automatically publishes all other writes to every possible observer.** Atomicity covers one operation on one location. Publishing a payload needs ordering: the producer's payload write must happen before a release on the flag, and the consumer must acquire the flag before reading the payload, at a scope that covers both parties. Worked example 2 shows a correct atomic count alongside an incomplete payload protocol, which is exactly the gap this mistake ignores.

## Self-check, retrieval and transfer

1. What are the four events in worked example 1's publication chain?
2. Why can block scope be too narrow?
3. What is the difference between visibility and atomicity?

Short answers are in the [separate explanations](../solutions/cuda-028_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-028: Memory ordering and atomic scope.
Read courses/cuda/cpp/guides/cuda-028.md and courses/cuda/cpp/lessons/cuda-028.md.
Direct prerequisites: `cuda-022`, `cuda-027`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-028_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-028_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
