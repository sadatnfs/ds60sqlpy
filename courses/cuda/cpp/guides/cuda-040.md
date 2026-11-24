# cuda-040: Pinned memory and overlapping transfer with compute

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-013`, `cuda-032`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement chunked double buffering with pinned host memory and show or explain the overlap on a timeline.

Work through *Pinned memory and overlapping transfer with compute* with the concrete cases below. Finish with this evidence:
correct chunk boundaries and a timeline that either demonstrates overlap or explains why the current device/workload does not overlap. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

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

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-040_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-040_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Three chunks each need 2 ms upload, 3 ms compute and 2 ms download. Fully serial time is 21 ms. An ideal three-stage pipeline takes 7 ms for the first result plus two 3 ms steady-state intervals, totaling 13 ms. This optimistic model assumes independent stages and sufficient engines/resources.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
chunks, upload, compute, download = 3, 2, 3, 2
serial = chunks * (upload + compute + download)
ideal = upload + compute + download + (chunks - 1) * max(upload, compute, download)
assert serial == 21 and ideal == 13
print({"synthetic_serial_ms": serial, "ideal_pipeline_ms": ideal, "measured_overlap": False})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'synthetic_serial_ms': 21, 'ideal_pipeline_ms': 13, 'measured_overlap': False}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

With two reusable slots, chunk 2 reuses chunk 0's slot only after chunk 0's download and host consumption are complete. Checking only compute completion can still overwrite an output that is being transferred or read. Ownership includes every stage, not just the kernel.

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

Compute ideal time for five chunks under the same stage costs.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can pinned allocation inside every iteration hurt?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if the final chunk is smaller?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose a chunk size for interactive requests.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **an API with `Async` in its name guarantees all useful work overlaps.**

For the concrete failure exercise, why can pinned allocation inside every iteration hurt?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-040_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
