# cuda-033: Nsight Compute: interpret kernel counters carefully

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-002`, `cuda-007`, `cuda-031`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Interpret Nsight Compute counters to support two claims and state one unresolved hypothesis.

**Scope:** Requested versus measured work, memory throughput, occupancy, eligible warps, instruction mix, replay and sampling overhead.

**Evidence to produce:** Two supported claims and one explicitly unresolved hypothesis.

## Purpose, vocabulary and mental model

Kernel counters describe selected aspects of execution, often through replay or sampled collection. They require context: achieved occupancy is a residency measurement, memory throughput measures traffic, and eligible-warps metrics describe scheduling opportunity. High utilization can mean an inefficient algorithm is busy moving unnecessary data. Low utilization can be expected for tiny work. Counter permissions are separate from ordinary CUDA execution capability; a working kernel does not promise profiler access. Start with a small question and a few relevant metrics, keeping the baseline's input, dtype and result contract fixed.

### Key terms

- **Achieved occupancy:** The measured average ratio of active warps to the maximum warps an SM supports.
- **Eligible warp:** A warp whose next instruction has its operands ready, so the scheduler can issue it this cycle.
- **Memory throughput:** The achieved rate of traffic at a memory level, often reported as a percentage of the hardware peak.
- **Kernel replay:** Re-running one kernel several times so a profiler can collect more counters than one pass allows.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-033_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-033_cpu.py
```

## Worked example 1: trace the mechanism

A synthetic kernel reads 400 useful bytes but causes 1,600 transferred bytes because of its access pattern. Useful-to-transferred ratio is 0.25. A high DRAM traffic counter does not imply useful data processing is efficient. Compare address patterns and a corrected layout before blaming arithmetic capacity.

**Why:** Only a quarter of moved bytes do useful work, so the access pattern wastes bandwidth.

```python
useful, transferred = 400, 1600
assert useful / transferred == 0.25
print({"useful_fraction": useful / transferred})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'useful_fraction': 0.25}
```

**Check:** The reference asserts useful / transferred == 0.25.

## Worked example 2: change a meaningful condition

Two kernels show 50% and 75% occupancy, yet times are 2 and 3 ms. Occupancy alone cannot rank them. The second may do more instructions, spill registers or repeat loads. Keep both correctness and selected counters with the timings, and state which causal explanation remains a hypothesis.

**Why:** The 75 percent kernel takes 3 ms against 2 ms, so occupancy did not predict speed.

**Check:** Keep correctness checks and counters next to each timing.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Divide 400 useful bytes by 1,600 transferred bytes.

**Trap to avoid:** Reading high DRAM throughput as efficient processing ignores that most bytes are unused.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Rank by measured time and use occupancy only to explain differences.

**Trap to avoid:** Picking the higher-occupancy kernel as faster contradicts the measured times.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Calculate useful throughput for 12 MB processed in 0.2 ms.

**Trap to avoid:** Using binary units here gives about 55.9 GiB/s and a mismatched label.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can a profiler run differ from an ordinary timing run?

**Trap to avoid:** Quoting a kernel time from an instrumented replay as normal runtime overstates cost.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if hardware counters are unavailable?

**Trap to avoid:** Estimating counter values and presenting them as measured fabricates evidence.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a counter-based investigation for strided reads.

**Trap to avoid:** Comparing a strided kernel with a contiguous one doing less work credits layout for reduced work.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A high utilization percentage proves the algorithm is efficient or any single metric diagnoses all bottlenecks.** A utilization percentage measures how busy a unit is, not whether the work is useful. Worked example 1 shows high DRAM traffic where only a quarter of the bytes are used, and worked example 2 shows higher occupancy with a slower kernel. Each counter answers a narrow question, so combine several counters with correctness checks and timing before naming a bottleneck, and label untested explanations as hypotheses. Here the counter points at the access pattern: a layout that transfers close to the 400 useful bytes could cut DRAM traffic by up to four times, while faster arithmetic would leave the 0.25 ratio unchanged.

## Self-check, retrieval and transfer

1. What fraction of transferred bytes is useful in worked example 1?
2. Why can a profiled kernel run slower than in a normal timing run?
3. What does achieved occupancy measure?
4. What should you report if counter access is not permitted?

Short answers are in the [separate explanations](../solutions/cuda-033_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
