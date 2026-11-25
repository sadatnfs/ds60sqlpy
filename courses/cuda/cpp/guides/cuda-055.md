# cuda-055: Cooperative Groups and global coordination

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-027`, `cuda-028`, `cuda-036`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Justify cooperative group participation with a written argument and a runtime capability report.

**Scope:** Group membership, collective contracts, block and tile groups, cooperative launch restrictions and residency.

**Evidence to produce:** A correct participation argument and runtime capability report.

## Purpose, vocabulary and mental model

Cooperative Groups makes participating thread groups explicit. A group collective is valid only when its membership and participation requirements are met. A block group can express block cooperation; a grid-wide group requires a supported cooperative launch and launch-size constraints. Ordinary launches cannot safely turn a hand-written spin loop into a global barrier. Device support, resource usage and residency determine whether a cooperative grid fits. Start with block-level algorithms and keep a multi-kernel fallback whose dependencies are established by normal launch ordering.

### Key terms

- **Cooperative Groups:** A CUDA API that names sets of threads explicitly and synchronizes them as groups.
- **Thread block tile:** A fixed-size partition of a block, such as 32 threads, created with `tiled_partition`.
- **Grid group:** A group representing every thread in the grid, which can synchronize only under a cooperative launch.
- **Cooperative launch:** A launch through `cudaLaunchCooperativeKernel` that guarantees all blocks are resident at once.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-055_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-055_cpu.py
```

## Worked example 1: trace the mechanism

An eight-thread conceptual block splits into two groups of four. Each group sums its values: \([1,2,3,4]\) gives ten and \([5,6,7,8]\) gives 26. The block-level final result is 36 after a separate valid combination step. Group-local synchronization does not synchronize the other group automatically.

**Why:** Group sums are 10 and 26, and their combination is 36.

```python
values = list(range(1, 9))
partials = [sum(values[start : start + 4]) for start in range(0, len(values), 4)]
assert partials == [10, 26] and sum(partials) == 36
assert 12 > 4 * 2
print({"group_sums": partials, "simplified_cooperative_capacity": 8})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'group_sums': [10, 26], 'simplified_cooperative_capacity': 8}
```

**Check:** The reference asserts partials == [10, 26] and their sum is 36.

## Worked example 2: change a meaningful condition

A simplified cooperative capacity is four SMs times two resident blocks per SM, or eight blocks. Requesting twelve cooperative blocks violates that assumed capacity. The actual supported limit must be obtained for the real kernel/device; source-level arithmetic is only an explanatory model.

**Why:** Twelve cooperative blocks exceed eight, so the launch is invalid under this model.

**Check:** Query the real occupancy API for the kernel and device before launch.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Split eight threads into two groups of four, sum each group, then combine in a separate step.

**Trap to avoid:** Assuming a group sync also orders the other group skips the combination step's ordering.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Multiply four SMs by two blocks per SM for a modeled capacity of eight.

**Trap to avoid:** Launching twelve and hoping some finish early can deadlock at the grid barrier.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Explain group size versus input count.

**Trap to avoid:** Removing tail threads from the group breaks the collective's membership.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can a grid barrier fail in an ordinary launch?

**Trap to avoid:** Calling a grid barrier in an ordinary launch can wait on unscheduled blocks forever.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if cooperative launch is unavailable?

**Trap to avoid:** Failing the whole lesson when the feature is missing removes a working path.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Refactor a reduction into explicit groups.

**Trap to avoid:** Assuming all threads participate when some are tails hides incorrect data.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Calling a grid barrier makes an ordinary launch globally synchronized.** A grid barrier is safe only under a supported cooperative launch, where every block is resident at the same time. In an ordinary launch some blocks may wait for others that cannot start until the waiting ones finish, so the program can hang. Worked example 2 shows twelve blocks exceeding an eight block capacity. Query the real limit for the kernel and device, or split the work into separate kernel launches whose boundary provides the global synchronization. Keep a CPU model of the group membership, as worked example 1 does, so each partial sum can be checked before the final combination.

## Self-check, retrieval and transfer

1. What are the group results and final total in worked example 1?
2. What is the assumed cooperative capacity in worked example 2?
3. What should a reduction do if cooperative launch is unavailable?
4. Why does group-local synchronization not combine the two groups?

Short answers are in the [separate explanations](../solutions/cuda-055_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [Cooperative Groups](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cooperative-groups.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-055: Cooperative Groups and global coordination.
Read courses/cuda/cpp/guides/cuda-055.md and courses/cuda/cpp/lessons/cuda-055.md.
Direct prerequisites: `cuda-027`, `cuda-028`, `cuda-036`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-055_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-055_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
