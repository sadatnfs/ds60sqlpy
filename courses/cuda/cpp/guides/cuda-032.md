# cuda-032: Nsight Systems: understand the application's timeline

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-031`, `cuda-025`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Interpret an Nsight Systems timeline to form a bottleneck hypothesis and test it with one experiment.

**Scope:** CPU submission, transfers, GPU kernels, idle gaps, synchronization, NVTX ranges and capture scope.

**Evidence to produce:** A timeline-supported bottleneck hypothesis and one experiment that tests it.

## Purpose, vocabulary and mental model

A timeline shows when the CPU submits work, when copies and kernels execute, and where synchronization or idle gaps occur. Begin with the application's critical path before optimizing an individual instruction. NVTX ranges can name phases such as upload, transform and download, but annotations must match real code boundaries. Nsight Systems collection needs an explicitly prepared environment and appropriate permissions. A captured or synthetic trace remains useful for reasoning on a CPU-only machine, provided its provenance is clear. A timeline suggests a hypothesis; a controlled change tests whether that hypothesis improves the desired metric.

### Key terms

- **Timeline:** A time-ordered view of CPU threads, API calls, copies and kernels that exposes gaps and overlap.
- **NVTX range:** A named annotation in code so a phase such as upload or transform appears on the timeline.
- **Critical path:** The longest chain of dependent work, which determines total elapsed time.
- **Idle gap:** A period with no device work queued, often caused by host synchronization or slow submission.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-032_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-032_cpu.py
```

## Worked example 1: trace the mechanism

A synthetic request contains upload 3 ms, kernel 2 ms, download 3 ms and host processing 2 ms, sequentially. Halving the kernel saves only 1 ms, changing total time from 10 to 9 ms. Eliminating an unnecessary round trip could offer a larger opportunity if semantics permit data to stay resident.

**Why:** The phases are sequential, so the total drops from 10 ms to 9 ms.

```python
phases = {"upload": 3, "kernel": 2, "download": 3, "host": 2}
total = sum(phases.values())
optimized = total - phases["kernel"] + phases["kernel"] / 2
assert total == 10 and optimized == 9
print({"synthetic_total_ms": total, "half_kernel_total_ms": optimized})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'synthetic_total_ms': 10, 'half_kernel_total_ms': 9.0}
```

**Check:** The reference asserts total == 10 and optimized == 9.

## Worked example 2: change a meaningful condition

A GPU sits idle for 6 ms between two 1 ms kernels while the host prepares data. Increasing the second kernel's occupancy does not remove that gap. Investigate host preparation, batching and dependencies, then measure the entire request again.

**Why:** The GPU waits on the host, so kernel speed does not limit this request.

**Check:** Measure the full request before and after a host-side change.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Sum upload 3, kernel 2, download 3 and host 2 ms, then halve only the kernel.

**Trap to avoid:** Expecting halving the kernel to halve the request ignores the 8 ms outside it.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Attack the 6 ms host-preparation gap rather than the 1 ms kernels.

**Trap to avoid:** Raising occupancy of the second kernel leaves the idle gap untouched.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Annotate the four phases of the 10 ms request.

**Trap to avoid:** Drawing the kernel as overlapping transfers misstates this synthetic model.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Can two bars overlap visually without the application getting faster?

**Trap to avoid:** Treating visual overlap as speedup skips measuring the request.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why separate the first iteration?

**Trap to avoid:** Averaging cold and warm runs together hides both behaviors.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Propose a one-change experiment for the idle-gap trace.

**Trap to avoid:** Changing several things at once makes any improvement impossible to attribute.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **The slowest-looking kernel is necessarily the greatest end-to-end optimization opportunity.** The end-to-end time depends on the critical path, not on the most prominent bar. Worked example 1 halves a 2 ms kernel and saves only 1 of 10 ms, because 6 ms are transfers and 2 ms are host work. Worked example 2 shows a 6 ms idle gap that no kernel tuning removes. Start with the timeline, find the largest serial cost on the path, and change that first. Removing an unneeded round trip could save up to the 6 ms of transfers, six times the kernel gain, if the data may stay resident on the device.

## Self-check, retrieval and transfer

1. In worked example 1, what saving would removing one 3 ms transfer give?
2. What does an idle gap on the GPU row usually point to?
3. Why must NVTX ranges match real code boundaries?
4. Why can two overlapping bars fail to speed up the application?

Short answers are in the [separate explanations](../solutions/cuda-032_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
