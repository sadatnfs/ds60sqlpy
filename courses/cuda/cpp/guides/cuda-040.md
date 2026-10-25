# cuda-040: Pinned memory and overlapping transfer with compute

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-013`, `cuda-032`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain pinned memory and overlapping transfer with compute using the concrete cases below. Produce correct chunk boundaries and a timeline that either demonstrates overlap or explains why the current device/workload does not overlap.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

Pinned host memory is page-locked storage that can support suitable asynchronous transfers. Pinning has a host resource cost, so use bounded reusable buffers rather than pinning arbitrary datasets. Overlap needs eligible transfers, independent work, compatible copy engines and correct dependencies. In double buffering, one slot can be computing while another is filled, but a producer must not overwrite a slot before its previous consumers finish. Chunk size trades fixed overhead against latency and memory. The word Async in an API name does not prove useful overlap occurred; a timeline supplies that evidence.

## Mathematical contract

\[
T_{\mathrm{ideal}}=u+c+d+(N-1)\max(u,c,d)
\]

For N chunks, u/c/d are upload, compute and download durations. This ideal pipeline assumes enough independent engines and correctly ordered reusable buffers.

## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/cuda-040_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-040_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

With two reusable slots, chunk 2 reuses chunk 0's slot only after chunk 0's download and host consumption are complete. Checking only compute completion can still overwrite an output that is being transferred or read. Ownership includes every stage, not just the kernel.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Start with the literal input and intermediate quantities in worked example 1.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Identify exactly which condition changes in worked example 2.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 3

Compute ideal time for five chunks under the same stage costs.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

Why can pinned allocation inside every iteration hurt?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What if the final chunk is smaller?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Choose a chunk size for interactive requests.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **an API with `Async` in its name guarantees all useful work overlaps.**

For the concrete failure exercise, why can pinned allocation inside every iteration hurt?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-040_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
