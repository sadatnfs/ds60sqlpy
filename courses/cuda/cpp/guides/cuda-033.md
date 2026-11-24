# cuda-033: Nsight Compute: interpret kernel counters carefully

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-002`, `cuda-007`, `cuda-031`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Interpret Nsight Compute counters to support two claims and state one unresolved hypothesis.

Work through *Nsight Compute: interpret kernel counters carefully* with the concrete cases below. Finish with this evidence:
two supported claims and one explicitly unresolved hypothesis. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Kernel counters describe selected aspects of execution, often through replay or sampled collection. They require context: achieved occupancy is a residency measurement, memory throughput measures traffic, and eligible-warps metrics describe scheduling opportunity. High utilization can mean an inefficient algorithm is busy moving unnecessary data. Low utilization can be expected for tiny work. Counter permissions are separate from ordinary CUDA execution capability; a working kernel does not promise profiler access. Start with a small question and a few relevant metrics, keeping the baseline's input, dtype and result contract fixed.

### Key terms

- **Achieved occupancy:** The measured average ratio of active warps to the maximum warps an SM supports.
- **Eligible warp:** A warp whose next instruction has its operands ready, so the scheduler can issue it this cycle.
- **Memory throughput:** The achieved rate of traffic at a memory level, often reported as a percentage of the hardware peak.
- **Kernel replay:** Re-running one kernel several times so a profiler can collect more counters than one pass allows.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-033_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-033_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A synthetic kernel reads 400 useful bytes but causes 1,600 transferred bytes because of its access pattern. Useful-to-transferred ratio is 0.25. A high DRAM traffic counter does not imply useful data processing is efficient. Compare address patterns and a corrected layout before blaming arithmetic capacity.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
useful, transferred = 400, 1600
assert useful / transferred == 0.25
print({"useful_fraction": useful / transferred})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'useful_fraction': 0.25}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Two kernels show 50% and 75% occupancy, yet times are 2 and 3 ms. Occupancy alone cannot rank them. The second may do more instructions, spill registers or repeat loads. Keep both correctness and selected counters with the timings, and state which causal explanation remains a hypothesis.

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

Calculate useful throughput for 12 MB processed in 0.2 ms.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can a profiler run differ from an ordinary timing run?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if hardware counters are unavailable?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a counter-based investigation for strided reads.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a high utilization percentage proves the algorithm is efficient or any single metric diagnoses all bottlenecks. .**

For the concrete failure exercise, why can a profiler run differ from an ordinary timing run?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-033_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [Nsight Compute profiling](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-033: Nsight Compute: interpret kernel counters carefully.
Read courses/cuda/cpp/guides/cuda-033.md and courses/cuda/cpp/lessons/cuda-033.md.
Direct prerequisites: `cuda-002`, `cuda-007`, `cuda-031`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-033_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-033_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
