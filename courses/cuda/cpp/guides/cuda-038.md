# cuda-038: Optimization review and a defensible benchmark

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-031`, `cuda-032`, `cuda-033`, `cuda-034`, `cuda-035`, `cuda-036`, `cuda-037`, `cuda-029`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Optimization review and a defensible benchmark* with the concrete cases below. Finish with this evidence:
reproducible report, retained raw data, error budget and a recommendation with its limits. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A defensible benchmark holds the problem contract fixed while changing one implementation decision. Record dtype, layout, supported shapes, numerical tolerance, data residency and required output. Compare against a competent baseline, not a deliberately poor CPU loop. Retain cold and warm measurements separately, avoid reporting only the fastest observation, and disclose device sharing, clocks and thermal conditions when relevant. A performance regression can coexist with improved kernel time if another phase grows. Report uncertainty and supported scope; no universal speed threshold is valid across every GPU and workload.

## Mathematical contract

\[
S_{\mathrm{median}}=\frac{\operatorname{median}(T_b)}{\operatorname{median}(T_c)}
\]

Use a consistent summary policy and retain both raw sample sets. The ratio is scoped to the actual experiment.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-038_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-038_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Baseline times are \([10,11,10,9,10]\) ms and candidate times \([8,8,9,8,7]\) ms. Median ratio is \(\frac{10}{8}=1.25\). This suggests an improvement for the measured fixture, but five synthetic samples do not establish stability across hardware, sizes or operating conditions.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

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

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'synthetic_median_speedup': 1.25, 'baseline_samples_ms': [10, 11, 10, 9, 10], 'candidate_samples_ms': [8, 8, 9, 8, 7]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A candidate uses float16 while the baseline uses float64. It may legitimately target a different accuracy budget, but it is not a like-for-like implementation comparison until both satisfy the same required error contract. Include conversion cost if the application supplies and consumes another dtype.

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

Write a benchmark contract for a 1,024-by-1,024 matrix product.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A report keeps only the minimum candidate time and median baseline time. Repair it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why include tiny and ragged shapes?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Decide whether to ship a faster but less accurate variant.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a single best run or one large speedup proves a universally superior implementation.**

For the concrete failure exercise, a report keeps only the minimum candidate time and median baseline time. Repair it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-038_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
