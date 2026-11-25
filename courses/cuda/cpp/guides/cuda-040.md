# cuda-040: Pinned memory and overlapping transfer with compute

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-013`, `cuda-032`, `cuda-039`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement chunked double buffering with pinned host memory and show or explain the overlap on a timeline.

**Scope:** Pageable versus pinned host memory, asynchronous transfer requirements, copy-engine limits, transfer directions and host-memory pressure.

**Evidence to produce:** Correct chunk boundaries and a timeline that either demonstrates overlap or explains why the current device/workload does not overlap.

## Purpose, vocabulary and mental model

Pinned host memory is page-locked storage that can support suitable asynchronous transfers. Pinning has a host resource cost, so use bounded reusable buffers rather than pinning arbitrary datasets. Overlap needs eligible transfers, independent work, compatible copy engines and correct dependencies. In double buffering, one slot can be computing while another is filled, but a producer must not overwrite a slot before its previous consumers finish. Chunk size trades fixed overhead against latency and memory. The word Async in an API name does not prove useful overlap occurred; a timeline supplies that evidence.

### Key terms

- **Pinned memory:** Page-locked host memory, allocated with `cudaMallocHost` or `cudaHostAlloc`, that the copy engine can transfer asynchronously.
- **cudaMemcpyAsync:** A copy that is queued in a stream and can overlap with other streams when the host buffer is pinned.
- **Double buffering:** Alternating two buffers so one chunk transfers while another is processed.
- **Chunk size:** The amount of data per transfer and compute step, which trades per-operation overhead against overlap.

## Mathematical contract

\[
T_{\mathrm{ideal}}=u+c+d+(N-1)\max(u,c,d)
\]

For N chunks, u/c/d are upload, compute and download durations. This ideal pipeline assumes enough independent engines and correctly ordered reusable buffers.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-040_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-040_cpu.py
```

## Worked example 1: trace the mechanism

Three chunks each need 2 ms upload, 3 ms compute and 2 ms download. Fully serial time is 21 ms. An ideal three-stage pipeline takes 7 ms for the first result plus two 3 ms steady-state intervals, totaling 13 ms. This optimistic model assumes independent stages and sufficient engines/resources.

**Why:** Once the pipeline fills, compute at 3 ms is the longest stage and sets the interval, giving 13 ms.

```python
chunks, upload, compute, download = 3, 2, 3, 2
serial = chunks * (upload + compute + download)
ideal = upload + compute + download + (chunks - 1) * max(upload, compute, download)
assert serial == 21 and ideal == 13
print({"synthetic_serial_ms": serial, "ideal_pipeline_ms": ideal, "measured_overlap": False})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'synthetic_serial_ms': 21, 'ideal_pipeline_ms': 13, 'measured_overlap': False}
```

**Check:** The reference asserts serial == 21 and ideal == 13 and marks measured_overlap False.

## Worked example 2: change a meaningful condition

With two reusable slots, chunk 2 reuses chunk 0's slot only after chunk 0's download and host consumption are complete. Checking only compute completion can still overwrite an output that is being transferred or read. Ownership includes every stage, not just the kernel.

**Why:** Two slots alternate, so chunk 2 overwrites memory chunk 0 may still be using.

**Check:** Add a per-slot done event recorded after host consumption and test with slow consumers.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Add 2 + 3 + 2 per chunk for 21 ms serial, then 7 ms for the first chunk plus two 3 ms intervals.

**Trap to avoid:** Dividing 21 by 3 stages for 7 ms assumes perfect overlap including fill and drain.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Reuse chunk 0's slot for chunk 2 only after chunk 0's download and host use finish.

**Trap to avoid:** Waiting only for chunk 0's compute lets the new upload overwrite data being downloaded.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute ideal time for five chunks under the same stage costs.

**Trap to avoid:** Multiplying 13 by five thirds assumes the fill cost repeats each chunk.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can pinned allocation inside every iteration hurt?

**Trap to avoid:** Allocating fresh pinned memory per chunk can erase the transfer gain.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if the final chunk is smaller?

**Trap to avoid:** Copying full slot size for the last chunk returns stale elements.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose a chunk size for interactive requests.

**Trap to avoid:** Choosing the largest chunk because throughput peaks violates response-time needs.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **An API with `Async` in its name guarantees all useful work overlaps.** The `Async` suffix means the call returns before the copy finishes. Real overlap also needs pinned host memory, a free copy engine, independent work in another stream and correct dependencies. With pageable memory the copy may block. Worked example 1 computes the ideal 13 ms only under all of those assumptions.

## Self-check, retrieval and transfer

1. What is the ideal time for four chunks with stage costs 2, 3 and 2 ms?
2. Why reuse pinned buffers instead of pinning in every iteration?
3. When may a double-buffering slot be refilled?

Short answers are in the [separate explanations](../solutions/cuda-040_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-040: Pinned memory and overlapping transfer with compute.
Read courses/cuda/cpp/guides/cuda-040.md and courses/cuda/cpp/lessons/cuda-040.md.
Direct prerequisites: `cuda-013`, `cuda-032`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-040_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-040_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
