# cuda-036: Occupancy, registers and latency hiding

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-002`, `cuda-019`, `cuda-033`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Choose a launch configuration for a stated workload and justify it even when the highest-occupancy setting loses.

**Scope:** Occupancy, active versus eligible warps, registers, shared-memory allocation, spills, instruction-level parallelism and work per thread.

**Evidence to produce:** A justified configuration choice for a stated workload and device, including an explanation when the highest-occupancy setting loses.

## Purpose, vocabulary and mental model

Occupancy compares resident warps with a hardware limit. Residency is constrained by threads, blocks, register allocation and shared memory, including allocation granularity. Resident does not mean ready to issue: a warp may wait for data or dependencies. More work per thread can improve reuse while increasing registers and reducing occupancy. Forcing fewer registers can increase spills to device memory. The goal is a correct faster workload, not maximizing one percentage. Use reviewed launch candidates, compiler resource reports and timings together, and avoid pretending a simplified resource arithmetic model reproduces every scheduling rule.

### Key terms

- **Occupancy:** The ratio of resident warps on an SM to the maximum it supports, limited by registers, shared memory and block size.
- **Register pressure:** High register use per thread that reduces how many warps can be resident at once.
- **Register spill:** Values the compiler moves to local memory when a thread needs more registers than are available.
- **Latency hiding:** Keeping the SM busy by switching to eligible warps while other warps wait for memory.
- **Launch bounds:** The `__launch_bounds__` qualifier that tells the compiler the maximum block size so it can limit registers.

## Mathematical contract

\[
N_{\mathrm{blocks}}\leq\left\lfloor\frac{R_{\mathrm{SM}}}{R_{\mathrm{thread}}T_{\mathrm{block}}}\right\rfloor
\]

This simplified register-only bound ignores allocation granularity and all other hardware limits. Do not report it as actual achieved occupancy.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-036_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-036_cpu.py
```

## Worked example 1: trace the mechanism

In a simplified SM with 65,536 registers, a 256-thread block using 64 registers per thread needs 16,384 registers. Registers alone permit four blocks. At 128 registers per thread, registers alone permit two. Other limits can reduce both figures; this calculation is not an actual occupancy API result.

**Why:** 256 * 64 is 16,384, so four blocks fit by registers; at 128 registers each block needs 32,768, so two fit.

```python
register_file, threads = 65536, 256
blocks = [register_file // (threads * registers) for registers in (64, 128)]
assert blocks == [4, 2]
print({"register_only_block_limits": blocks, "other_hardware_limits_included": False})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'register_only_block_limits': [4, 2], 'other_hardware_limits_included': False}
```

**Check:** The reference asserts blocks == [4, 2] and prints other_hardware_limits_included False.

## Worked example 2: change a meaningful condition

Configuration A takes 2 ms with 50% occupancy. Configuration B takes 2.4 ms with 75%. If both pass correctness, A wins that stated timing objective. Investigate reuse, instruction-level parallelism and spills rather than choosing B merely because its percentage is larger.

**Why:** The objective is time, and A wins it despite lower occupancy.

**Check:** Keep both timing distributions and resource reports together with the decision.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Divide 65,536 registers by 256 threads times registers per thread for 64 and 128 registers.

**Trap to avoid:** Treating four blocks as the final residency ignores shared memory, thread and block limits that may bind first.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Choose A because it meets correctness and takes 2 ms against 2.4 ms.

**Trap to avoid:** Picking B for its 75 percent occupancy confuses a resource metric with the goal.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Estimate register-limited blocks for 128 threads at 64 registers using 65,536 registers.

**Trap to avoid:** Reusing the 256-thread answer of four blocks ignores that the block is half as large.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why might reducing a register limit make a kernel slower?

**Trap to avoid:** Assuming more resident warps always hides the extra traffic ignores that spills sit on the critical path.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What limits an extremely small grid?

**Trap to avoid:** Raising per-block occupancy for a two-block grid cannot use the remaining SMs.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a launch sweep.

**Trap to avoid:** Changing tile size and block size together in one sweep mixes two effects.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **100 percent occupancy is always the best target.** Occupancy is a means of hiding latency, not the goal. Worked example 2 shows a 50% configuration beating a 75% one, because more work per thread can give reuse and instruction-level parallelism. Forcing fewer registers to raise occupancy can also cause spills that cost more than they save.

## Self-check, retrieval and transfer

1. How many 256-thread blocks fit by registers at 32 registers per thread with 65,536 registers?
2. What is the difference between a resident warp and an eligible warp?
3. What does a register spill cost?

Short answers are in the [separate explanations](../solutions/cuda-036_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-036: Occupancy, registers and latency hiding.
Read courses/cuda/cpp/guides/cuda-036.md and courses/cuda/cpp/lessons/cuda-036.md.
Direct prerequisites: `cuda-002`, `cuda-019`, `cuda-033`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-036_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-036_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
