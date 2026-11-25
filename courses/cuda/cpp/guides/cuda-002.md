# cuda-002: Meet the hardware without memorizing a product catalog

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-001`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Label a hardware and software map that separates SMs, warps, memory levels and compute capability.

**Scope:** CPU cores, GPU streaming multiprocessors, warps, arithmetic pipelines, registers, shared memory, caches, device memory, copy engines and host interconnect.

**Evidence to produce:** Labeled hardware/software map and a capability report if hardware exists.

## Purpose, vocabulary and mental model

An SM, or streaming multiprocessor, schedules groups of GPU threads and owns finite execution and storage resources. A block is a cooperating group in your program; it is not a physical processor. Blocks can wait for resources and need not run in index order. Within a block, threads are organized into warps, normally 32 threads in CUDA. A warp issues instructions with a set of participating lanes. Registers hold per-thread working values, shared memory supports block cooperation, and device DRAM holds larger arrays. Copy engines may transfer data while computation proceeds, but concurrency depends on hardware and dependencies. Compute capability identifies a hardware feature family; toolkit version identifies software.

### Key terms

- **Streaming multiprocessor (SM):** A GPU processing unit that schedules warps and owns finite registers, shared memory and execution pipelines.
- **Warp:** A group of 32 threads that an SM schedules together when it issues instructions.
- **Thread block:** A programmer-defined group of threads that runs on one SM and can cooperate through shared memory and barriers.
- **Compute capability:** A version number that identifies a GPU architecture's hardware feature set, separate from the toolkit version.
- **Copy engine:** A hardware unit that moves data between host and device memory and may overlap transfers with computation.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-002_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-002_cpu.py
```

## Worked example 1: trace the mechanism

Draw four SM boxes and a grid of ten blocks. Under the deliberately simplified assumption of one resident block per SM, the grid needs at least three waves: four, four and two blocks. This is an occupancy illustration, not a runtime prediction. Real residency depends on registers, shared memory, threads and architectural limits.

**Why:** With at most four blocks running at once, ten blocks need ceil(10 / 4) = 3 rounds: four, four, then two.

```python
from math import ceil

assert ceil(10 / 4) == 3
assert [ceil(n / 32) for n in (31, 32, 33, 100)] == [1, 1, 2, 4]
print({"simplified_waves": ceil(10 / 4), "warps_for_100_threads": ceil(100 / 32)})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'simplified_waves': 3, 'warps_for_100_threads': 4}
```

**Check:** The reference asserts ceil(10 / 4) == 3 and prints simplified_waves 3; redraw with five SMs and expect two waves.

## Worked example 2: change a meaningful condition

A block with 100 threads occupies four warps. The last warp contains four valid program threads and 28 unused lane positions. A kernel with 100 blocks does not require 10,000 physical arithmetic units. Scheduling reuses execution resources over time. Do not build a dependency that assumes block 0 finishes first.

**Why:** Warps are allocated whole, so 96 threads fill three warps and the remaining 4 threads occupy a fourth with 28 idle lanes.

**Check:** Check ceil(100 / 32) == 4 from the reference output and verify 100 - 3 * 32 = 4 active lanes in the last warp.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Assign ten blocks to four SM boxes one at a time under the stated one-resident-block rule and count rounds until every block has run.

**Trap to avoid:** Reading the drawing as a timing forecast fails because real residency per SM depends on registers, shared memory and thread limits.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Divide 100 threads by the warp width of 32 with ceiling division, then count valid lanes in the final warp.

**Trap to avoid:** Using floor division gives three warps and silently drops threads 96 to 99, which then never compute their outputs.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Calculate the warp count for blocks with 31, 32 and 33 threads.

**Trap to avoid:** Assuming 33 threads costs barely more than 32 hides that the second warp still occupies a whole scheduling slot for one lane.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A program labels its toolkit version as the GPU compute capability. Repair the inventory.

**Trap to avoid:** Copying the toolkit string into the capability field makes an inventory claim, for example 12.4, that no GPU actually reports.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Can ten blocks require more than three waves in the four-SM drawing?

**Trap to avoid:** Treating three waves as an exact count would wrongly reject a measured run that shows a staggered fourth group.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Map a 2 MiB array through host memory, transfer engine, device DRAM and an SM.

**Trap to avoid:** Passing the host pointer straight to a kernel assumes unified addressing makes host data resident; without managed memory that is an illegal access.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Every launched thread occupies its own permanent physical core.** Threads are a programming abstraction that the hardware schedules in warps onto a limited set of SMs over time. Worked example 2 shows a 100-thread block filling four warps, with 28 idle lanes, and 100 blocks reusing the same execution units in waves rather than claiming 10,000 permanent cores.

## Self-check, retrieval and transfer

1. How many warps does a block of 65 threads occupy, and how many lanes sit idle?
2. Why is a block not the same thing as an SM?
3. What does the copy engine add to the hardware picture?

Short answers are in the [separate explanations](../solutions/cuda-002_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-002: Meet the hardware without memorizing a product catalog.
Read courses/cuda/cpp/guides/cuda-002.md and courses/cuda/cpp/lessons/cuda-002.md.
Direct prerequisites: `cuda-001`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-002_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-002_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
