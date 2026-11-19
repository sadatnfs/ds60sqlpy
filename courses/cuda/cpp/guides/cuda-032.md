# cuda-032: Nsight Systems: understand the application's timeline

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-031`, `cuda-025`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Nsight Systems: understand the application's timeline* with the concrete cases below. Finish with this evidence:
a timeline-supported bottleneck hypothesis and one experiment that tests it. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A timeline shows when the CPU submits work, when copies and kernels execute, and where synchronization or idle gaps occur. Begin with the application's critical path before optimizing an individual instruction. NVTX ranges can name phases such as upload, transform and download, but annotations must match real code boundaries. Nsight Systems collection needs an explicitly prepared environment and appropriate permissions. A captured or synthetic trace remains useful for reasoning on a CPU-only machine, provided its provenance is clear. A timeline suggests a hypothesis; a controlled change tests whether that hypothesis improves the desired metric.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-032_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-032_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A synthetic request contains upload 3 ms, kernel 2 ms, download 3 ms and host processing 2 ms, sequentially. Halving the kernel saves only 1 ms, changing total time from 10 to 9 ms. Eliminating an unnecessary round trip could offer a larger opportunity if semantics permit data to stay resident.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
phases = {"upload": 3, "kernel": 2, "download": 3, "host": 2}
total = sum(phases.values())
optimized = total - phases["kernel"] + phases["kernel"] / 2
assert total == 10 and optimized == 9
print({"synthetic_total_ms": total, "half_kernel_total_ms": optimized})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'synthetic_total_ms': 10, 'half_kernel_total_ms': 9.0}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A GPU sits idle for 6 ms between two 1 ms kernels while the host prepares data. Increasing the second kernel's occupancy does not remove that gap. Investigate host preparation, batching and dependencies, then measure the entire request again.

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

Annotate the four phases of the 10 ms request.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Can two bars overlap visually without the application getting faster?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why separate the first iteration?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Propose a one-change experiment for the idle-gap trace.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **the slowest-looking kernel is necessarily the greatest end-to-end optimization opportunity. .**

For the concrete failure exercise, can two bars overlap visually without the application getting faster?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-032_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [Nsight Systems guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-032: Nsight Systems: understand the application's timeline.
Read courses/cuda/cpp/guides/cuda-032.md and courses/cuda/cpp/lessons/cuda-032.md.
Direct prerequisites: `cuda-031`, `cuda-025`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-032_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-032_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
