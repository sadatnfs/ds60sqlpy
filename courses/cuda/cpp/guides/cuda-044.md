# cuda-044: Second capstone: a streaming numerical service core

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-038`, `cuda-039`, `cuda-040`, `cuda-041`, `cuda-042`, `cuda-043`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Build a bounded streaming compute core that keeps memory within budget and reports latency separately from throughput.

**Scope:** Bounded queues, backpressure, chunk ownership, latency versus throughput, batching and cancellation.

**Evidence to produce:** All outputs match, no chunk is dropped or reused early, memory stays within the budget, and the report separates request latency from throughput.

## Purpose, vocabulary and mental model

A streaming compute service needs bounded ownership and backpressure before it needs more streams. Backpressure means producers stop or reject work when the system cannot safely accept another item. A slot moves through states such as free, filling, computing, copying and consumed. Reuse is allowed only after the final consumer completes. Cancellation stops admission and cleans up according to actual completion state; it does not magically cancel every submitted device instruction. This capstone is a bounded local pipeline, not a new network server inside the classroom worker.

### Key terms

- **Backpressure:** Refusing or delaying new requests when all buffers are busy, so memory use stays bounded.
- **Slot state machine:** A fixed set of buffer slots, each moving through explicit states such as free, uploading, computing and draining.
- **Request latency:** The time from accepting one request until its result is returned.
- **Memory budget:** The declared maximum device and pinned host memory the service may hold at once.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-044_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-044_cpu.py
```

## Worked example 1: trace the mechanism

With capacity two, submit chunks A and B. Chunk C waits until a slot becomes free. If A finishes compute but its output is still downloading, A's slot is not yet free. A correct queue can process arbitrary many chunks with constant bounded storage by reusing only completed slots.

**Why:** A slot is free only after its output download and host consumption complete, not after compute.

```python
states = ["free", "filling", "computing", "copying", "consumed", "free"]
assert states.index("computing") < states.index("consumed")
chunks = [[1, 2], [3], [], [4, 5]]
results = [[2 * x for x in chunk] for chunk in chunks]
assert results == [[2, 4], [6], [], [8, 10]]
print({"reference_results": results, "slot_lifecycle": states})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'reference_results': [[2, 4], [6], [], [8, 10]], 'slot_lifecycle': ['free', 'filling', 'computing', 'copying', 'consumed', 'free']}
```

**Check:** The reference doubles [[1, 2], [3], [], [4, 5]] to [[2, 4], [6], [], [8, 10]]; match each chunk's output.

## Worked example 2: change a meaningful condition

A synchronous pipeline has 7 ms latency per chunk. A pipelined version can deliver later chunks every 3 ms while the first still takes roughly 7 ms in the ideal model. Throughput and first-result latency are distinct objectives; reporting only the inter-result interval hides the user's wait.

**Why:** Pipelining raises throughput while the first chunk still passes through every stage.

**Check:** Measure time to first output and time between outputs on a GPU.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Admit chunks A and B into two slots, and hold C until a slot reaches the free state.

**Trap to avoid:** Freeing A's slot when its kernel finishes lets C's upload overwrite output still downloading.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Report first-result latency of about 7 ms and steady interval of about 3 ms separately.

**Trap to avoid:** Quoting 3 ms as the latency of each request hides the 7 ms a single caller waits.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Write legal transitions for a two-slot pipeline.

**Trap to avoid:** Allowing computing to return to free skips copying and consumption.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A cancellation handler immediately frees all device buffers. What is missing?

**Trap to avoid:** Freeing immediately on cancel leaves in-flight operations reading released memory.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should happen to a zero-length chunk?

**Trap to avoid:** Dropping the empty chunk shifts every later output to the wrong input.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Define capstone acceptance beyond timing.

**Trap to avoid:** Accepting the capstone on throughput alone skips the failures users would notice.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Maximizing batch size automatically gives the best user experience.** Larger batches raise throughput but make each request wait longer for its batch to fill and finish. Worked example 2 separates first-result latency, about 7 ms, from the 3 ms interval between later results. An interactive service needs a latency target and backpressure, not the largest batch that fits.

## Self-check, retrieval and transfer

1. When is a slot free in worked example 1?
2. What does backpressure do?
3. What must cancellation do before freeing device buffers?

Short answers are in the [separate explanations](../solutions/cuda-044_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-044: Second capstone: a streaming numerical service core.
Read courses/cuda/cpp/guides/cuda-044.md and courses/cuda/cpp/lessons/cuda-044.md.
Direct prerequisites: `cuda-038`, `cuda-039`, `cuda-040`, `cuda-041`, `cuda-042`, `cuda-043`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-044_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-044_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
