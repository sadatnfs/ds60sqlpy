# cuda-007: From elapsed time to a performance model

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-001`, `cuda-005`, `cuda-006`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Build a units-correct roofline estimate and design an experiment that could disprove it.

Work through *From elapsed time to a performance model* with the concrete cases below. Finish with this evidence:
a units-correct model and an experiment that could disprove it. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Arithmetic intensity measures operations per byte of data movement under an explicitly stated memory model. A roofline estimate limits performance by the smaller of arithmetic capacity and bandwidth times intensity. It is an upper bound, not a timer. Vector addition reads two float32 values and writes one for one addition, giving roughly one operation per twelve useful bytes before cache and transaction effects. Matrix multiplication can reuse each loaded value many times; tiling increases reuse but consumes working storage. Launch cost, transfer cost, dependency stalls and imperfect access patterns can keep measured work far below either bound.

### Key terms

- **Arithmetic intensity:** Operations performed per byte moved under a stated memory model, measured in FLOP per byte.
- **Roofline model:** An upper bound on performance set by the smaller of peak arithmetic rate and bandwidth times arithmetic intensity.
- **Memory bandwidth:** The maximum rate at which data moves between memory and the processors, in bytes per second.
- **Launch overhead:** The fixed host and device cost of submitting a kernel, which dominates very small workloads.

## Mathematical contract

\[
P\leq\min(P_{\mathrm{peak}},B I)
\]

P is operations per second, B is bytes per second, and I is operations per byte under the stated traffic model. This bound omits fixed overhead and many implementation effects.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-007_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-007_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Assume hypothetical bandwidth of 600 GB/s, using decimal billions, and a 12-byte-per-element vector addition. The ideal useful-element throughput is 50 billion elements/s. One million elements require at least 20 microseconds at that bandwidth, excluding launch and host transfer. This is a thought experiment, not a claim about the learner's GPU.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
n, bytes_per_element, bandwidth = 1_000_000, 12, 600e9
seconds = n * bytes_per_element / bandwidth
assert abs(seconds - 20e-6) < 1e-15
limits = [min(10e12, intensity * 500e9) for intensity in (2, 40)]
assert limits == [1e12, 10e12]
print({"ideal_memory_seconds": seconds, "roofline_flops_per_second": limits})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'ideal_memory_seconds': 2e-05, 'roofline_flops_per_second': [1000000000000.0, 10000000000000.0]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A hypothetical device has 10 TFLOP/s arithmetic capacity and 500 GB/s bandwidth. At intensity 2 FLOP/byte the roofline is 1 TFLOP/s; at intensity 40 it is capped at 10 TFLOP/s. Increasing reuse can change the limiting resource, but a kernel must still expose sufficient independent work.

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

Estimate useful bytes for adding two length-1,000 float64 vectors.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A calculation divides bytes by TFLOP/s and calls the result seconds. Diagnose it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why is a roofline less useful for a one-element kernel?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

A tiled kernel reduces global reads but doubles register use. What evidence decides?

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **peak TFLOPS predicts every kernel, or a kernel speedup is automatically an application speedup.**

For the concrete failure exercise, a calculation divides bytes by TFLOP/s and calls the result seconds. Diagnose it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-007_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-007: From elapsed time to a performance model.
Read courses/cuda/cpp/guides/cuda-007.md and courses/cuda/cpp/lessons/cuda-007.md.
Direct prerequisites: `cuda-001`, `cuda-005`, `cuda-006`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-007_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-007_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
