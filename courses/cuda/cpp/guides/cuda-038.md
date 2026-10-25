# cuda-038: Optimization review and a defensible benchmark

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-031`, `cuda-032`, `cuda-033`, `cuda-034`, `cuda-035`, `cuda-036`, `cuda-037`, `cuda-029`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain optimization review and a defensible benchmark using the concrete cases below. Produce reproducible report, retained raw data, error budget and a recommendation with its limits.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

A defensible benchmark holds the problem contract fixed while changing one implementation decision. Record dtype, layout, supported shapes, numerical tolerance, data residency and required output. Compare against a competent baseline, not a deliberately poor CPU loop. Retain cold and warm measurements separately, avoid reporting only the fastest observation, and disclose device sharing, clocks and thermal conditions when relevant. A performance regression can coexist with improved kernel time if another phase grows. Report uncertainty and supported scope; no universal speed threshold is valid across every GPU and workload.

## Mathematical contract

\[
S_{\mathrm{median}}=\frac{\operatorname{median}(T_b)}{\operatorname{median}(T_c)}
\]

Use a consistent summary policy and retain both raw sample sets. The ratio is scoped to the actual experiment.

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
The separate [CPU reference](../references/cuda-038_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-038_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A candidate uses float16 while the baseline uses float64. It may legitimately target a different accuracy budget, but it is not a like-for-like implementation comparison until both satisfy the same required error contract. Include conversion cost if the application supplies and consumes another dtype.

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

Write a benchmark contract for a 1,024-by-1,024 matrix product.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

A report keeps only the minimum candidate time and median baseline time. Repair it.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

Why include tiny and ragged shapes?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Decide whether to ship a faster but less accurate variant.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a single best run or one large speedup proves a universally superior implementation.**

For the concrete failure exercise, a report keeps only the minimum candidate time and median baseline time. Repair it.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-038_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
