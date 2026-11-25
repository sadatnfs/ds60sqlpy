# cuda-007: From elapsed time to a performance model

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-001`, `cuda-005`, `cuda-006`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Build a units-correct roofline estimate and design an experiment that could disprove it.

**Scope:** FLOPs, bytes moved, arithmetic intensity, bandwidth, launch overhead, warm versus cold state, and kernel time versus end-to-end time.

**Evidence to produce:** A units-correct model and an experiment that could disprove it.

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

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-007_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-007_cpu.py
```

## Worked example 1: trace the mechanism

Assume hypothetical bandwidth of 600 GB/s, using decimal billions, and a 12-byte-per-element vector addition. The ideal useful-element throughput is 50 billion elements/s. One million elements require at least 20 microseconds at that bandwidth, excluding launch and host transfer. This is a thought experiment, not a claim about the learner's GPU.

**Why:** Vector add reads two float32 values and writes one, so 12 bytes per element is the useful traffic floor.

```python
n, bytes_per_element, bandwidth = 1_000_000, 12, 600e9
seconds = n * bytes_per_element / bandwidth
assert abs(seconds - 20e-6) < 1e-15
limits = [min(10e12, intensity * 500e9) for intensity in (2, 40)]
assert limits == [1e12, 10e12]
print({"ideal_memory_seconds": seconds, "roofline_flops_per_second": limits})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'ideal_memory_seconds': 2e-05, 'roofline_flops_per_second': [1000000000000.0, 10000000000000.0]}
```

**Check:** The reference asserts the time is within 1e-15 of 20e-6 seconds and prints ideal_memory_seconds 2e-05.

## Worked example 2: change a meaningful condition

A hypothetical device has 10 TFLOP/s arithmetic capacity and 500 GB/s bandwidth. At intensity 2 FLOP/byte the roofline is 1 TFLOP/s; at intensity 40 it is capped at 10 TFLOP/s. Increasing reuse can change the limiting resource, but a kernel must still expose sufficient independent work.

**Why:** At 2 FLOP/byte bandwidth allows 1 TFLOP/s, below the compute ceiling; at 40 the product 20 TFLOP/s is capped at 10.

**Check:** The reference asserts limits == [1e12, 10e12]; the ridge point 10e12 / 500e9 = 20 FLOP/byte separates the regimes.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Multiply one million elements by 12 bytes, giving 12 MB, and divide by 600e9 bytes per second.

**Trap to avoid:** Dividing by 600 GiB/s instead of decimal GB/s shifts the answer by about 7 percent and mixes unit systems.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Compute min(10 TFLOP/s, intensity times 500 GB/s) separately for intensity 2 and intensity 40.

**Trap to avoid:** Quoting 10 TFLOP/s for both kernels ignores that the low-intensity kernel starves for bytes long before arithmetic saturates.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Estimate useful bytes for adding two length-1,000 float64 vectors.

**Trap to avoid:** Using 4-byte elements from the float32 example gives 12,000 bytes, half the real payload for float64.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A calculation divides bytes by TFLOP/s and calls the result seconds. Diagnose it.

**Trap to avoid:** Converting TFLOP/s to bytes by assuming one byte per FLOP invents an intensity that the kernel does not have.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why is a roofline less useful for a one-element kernel?

**Trap to avoid:** Plotting the single-element kernel on a roofline predicts near-zero time and makes any measurement look like a defect.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

A tiled kernel reduces global reads but doubles register use. What evidence decides?

**Trap to avoid:** Accepting the tiled version because estimated bytes fell skips both correctness and the occupancy trade.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Peak TFLOPS predicts every kernel, or a kernel speedup is automatically an application speedup.** Peak arithmetic is only one roof. Worked example 2 shows a kernel at intensity 2 FLOP/byte capped at 1 TFLOP/s by bandwidth on a 10 TFLOP/s device, and launch overhead or transfers can dominate an application even when the kernel itself speeds up.

## Self-check, retrieval and transfer

1. What useful byte count does vector addition of n float32 elements move?
2. At what intensity does the worked example 2 device switch from bandwidth bound to compute bound?
3. Why must kernel time and end-to-end time be reported separately?

Short answers are in the [separate explanations](../solutions/cuda-007_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
