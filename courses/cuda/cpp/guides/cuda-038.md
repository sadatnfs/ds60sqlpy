# cuda-038: Optimization review and a defensible benchmark

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-031`, `cuda-032`, `cuda-033`, `cuda-034`, `cuda-035`, `cuda-036`, `cuda-037`, `cuda-029`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Produce a reproducible benchmark report with retained raw data, an error budget and a limited recommendation.

**Scope:** One-variable experiments, statistical uncertainty, baseline fairness, warm/cold scenarios, power and thermal state, hardware provenance and regressions.

**Evidence to produce:** Reproducible report, retained raw data, error budget and a recommendation with its limits.

## Purpose, vocabulary and mental model

A defensible benchmark holds the problem contract fixed while changing one implementation decision. Record dtype, layout, supported shapes, numerical tolerance, data residency and required output. Compare against a competent baseline, not a deliberately poor CPU loop. Retain cold and warm measurements separately, avoid reporting only the fastest observation, and disclose device sharing, clocks and thermal conditions when relevant. A performance regression can coexist with improved kernel time if another phase grows. Report uncertainty and supported scope; no universal speed threshold is valid across every GPU and workload.

### Key terms

- **Competent baseline:** A reasonable optimized comparison implementation instead of a deliberately weak one.
- **Problem contract:** The fixed definition of inputs, outputs, accuracy and timing scope that every compared version must satisfy.
- **Raw samples:** The individual timing measurements kept alongside any summary statistic.
- **Thermal throttling:** A clock reduction caused by heat or power limits that changes performance during a run.

## Mathematical contract

\[
S_{\mathrm{median}}=\frac{\operatorname{median}(T_b)}{\operatorname{median}(T_c)}
\]

Use a consistent summary policy and retain both raw sample sets. The ratio is scoped to the actual experiment.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-038_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-038_cpu.py
```

## Worked example 1: trace the mechanism

Baseline times are \([10,11,10,9,10]\) ms and candidate times \([8,8,9,8,7]\) ms. Median ratio is \(\frac{10}{8}=1.25\). This suggests an improvement for the measured fixture, but five synthetic samples do not establish stability across hardware, sizes or operating conditions.

**Why:** Medians of 10 ms and 8 ms give 1.25 for this fixture.

```python
import statistics

baseline, candidate = [10, 11, 10, 9, 10], [8, 8, 9, 8, 7]
speedup = statistics.median(baseline) / statistics.median(candidate)
assert speedup == 1.25
print(
    {
        "synthetic_median_speedup": speedup,
        "baseline_samples_ms": baseline,
        "candidate_samples_ms": candidate,
    }
)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'synthetic_median_speedup': 1.25, 'baseline_samples_ms': [10, 11, 10, 9, 10], 'candidate_samples_ms': [8, 8, 9, 8, 7]}
```

**Check:** The reference asserts the median speedup equals 1.25.

## Worked example 2: change a meaningful condition

A candidate uses float16 while the baseline uses float64. It may legitimately target a different accuracy budget, but it is not a like-for-like implementation comparison until both satisfy the same required error contract. Include conversion cost if the application supplies and consumes another dtype.

**Why:** float16 changes accuracy and conversion cost, so its speed is a different trade.

**Check:** Measure error against a reference for both and include conversions in timing.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Take the median of each sample set and divide 10 by 8.

**Trap to avoid:** Claiming a general 25 percent improvement from five synthetic samples overstates what they show.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Hold both versions to the same error contract before comparing speed.

**Trap to avoid:** Reporting float16 against float64 as a like-for-like speedup hides the accuracy loss.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Write a benchmark contract for a 1,024-by-1,024 matrix product.

**Trap to avoid:** Writing only the matrix size lets two runs differ in dtype or layout.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A report keeps only the minimum candidate time and median baseline time. Repair it.

**Trap to avoid:** Dropping baseline outliers while keeping candidate ones biases the result.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why include tiny and ragged shapes?

**Trap to avoid:** Testing only 1,024 aligned sizes hides costs real requests pay.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Decide whether to ship a faster but less accurate variant.

**Trap to avoid:** Shipping because typical inputs look fine leaves edge inputs unprotected.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A single best run or one large speedup proves a universally superior implementation.** One fast run can reflect a lucky clock state, a warm cache or a different accuracy target. Worked example 1 compares medians of five samples each and still limits the claim to that fixture, and worked example 2 shows float16 against float64 is not like for like. A defensible claim keeps raw samples, a competent baseline and the same error contract.

## Self-check, retrieval and transfer

1. Why compare medians rather than the fastest run of each version?
2. What makes a CPU baseline competent?
3. Why record thermal state and device sharing?

Short answers are in the [separate explanations](../solutions/cuda-038_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-038: Optimization review and a defensible benchmark.
Read courses/cuda/cpp/guides/cuda-038.md and courses/cuda/cpp/lessons/cuda-038.md.
Direct prerequisites: `cuda-031`, `cuda-032`, `cuda-033`, `cuda-034`, `cuda-035`, `cuda-036`, `cuda-037`, `cuda-029`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-038_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-038_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
