# cuda-001: What a GPU accelerates, and what it cannot make fast

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: None within this subject. Basic loops and arrays help; revisit Python or C++ foundations when needed.

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Decide whether to accelerate or keep each of two tasks on the CPU using an end-to-end Amdahl model.

**Scope:** Distinguish latency from throughput, independent tasks from dependent chains, and parallelizable work from serial overhead.

**Evidence to produce:** A decomposition diagram and a justified decision to accelerate or keep two tasks on CPU.

## Purpose, vocabulary and mental model

A CPU is optimized to make progress on a comparatively small number of complicated instruction streams. A GPU spends more of its resources on throughput across many pieces of work. This is a design distinction, not a rule that the GPU wins. A dependency means that one result must exist before another calculation can start. Pixel brightness updates have independent destinations; a running account balance has a dependency between successive balances. There can still be a parallel prefix algorithm for that balance, but changing the algorithm is real work. Include loading data, launching kernels and returning results when deciding whether acceleration helps a person waiting for an answer.

### Key terms

- **Throughput:** The amount of completed work per unit of time across many independent pieces of work, which GPU designs favor.
- **Latency:** The time from submitting one piece of work until its result is available, including transfer and launch costs.
- **Data dependency:** A relationship in which one calculation needs another calculation's result before it can start.
- **Amdahl's law:** A bound on whole-application speedup set by the fraction of time that stays serial or unaccelerated.

## Mathematical contract

\[
T_{\mathrm{new}}=T_{\mathrm{serial}}+\frac{T_{\mathrm{parallel}}}{s}+T_{\mathrm{transfer}}
\]

Times use the same units; s is the speedup of only the parallel portion. Launch and other overhead must also be included when present.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-001_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-001_cpu.py
```

## Worked example 1: trace the mechanism

Suppose an application spends 20 seconds parsing and 80 seconds transforming pixels. An imagined GPU makes the transform ten times faster and adds 4 seconds of transfers. The new time is \(20 + 8 + 4 = 32\) seconds, so the application speedup is 3.125. The tenfold kernel improvement is not the application improvement. Even an infinitely fast transform leaves 24 seconds under these assumptions.

**Why:** Amdahl's model divides only the accelerated phase, so parsing stays at 20 seconds and the added copies count against the 32-second total.

```python
cpu = 20 + 80
gpu = 20 + 80 / 10 + 4
assert gpu == 32
assert cpu / gpu == 3.125
print({"CPU_seconds": cpu, "modeled_GPU_seconds": gpu, "speedup": cpu / gpu})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'CPU_seconds': 100, 'modeled_GPU_seconds': 32.0, 'speedup': 3.125}
```

**Check:** Run the CPU reference: its assertions require gpu == 32 and cpu / gpu == 3.125, and the printed dictionary shows modeled_GPU_seconds 32.0.

## Worked example 2: change a meaningful condition

For one tiny request, suppose CPU arithmetic costs 2 microseconds, while GPU submission and transfers cost 30 microseconds before arithmetic. A 0.2 microsecond kernel gives 30.2 microseconds end to end. Batching 1,000 independent requests may amortize overhead, but it changes waiting time and memory usage. Neither result follows from a core count.

**Why:** A single request waits for every phase in sequence, so fixed launch and copy overhead dominate when the arithmetic itself is only two microseconds.

**Check:** Recompute 30 + 0.2 by hand, then recompute per-request overhead for a batch of 1,000 and note the extra queueing delay it introduces.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Split the 100-second run into its 20-second parse, 80-second transform and the new 4-second transfer, then rescale only the transform by ten.

**Trap to avoid:** Dividing the whole 100 seconds by ten predicts 10 seconds; that silently accelerates the parser and forgets the 4 seconds of copies.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Add the 30 microseconds of submission and transfer to the 0.2 microsecond kernel and compare that 30.2 sum with 2 microseconds of CPU arithmetic.

**Trap to avoid:** Comparing 0.2 against 2 and claiming a tenfold win measures the kernel alone; the requester still waits more than fifteen times longer.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Construct a 100-second workload with 60 seconds parallelizable and no transfer cost; compute the best possible speedup.

**Trap to avoid:** Answering 60 or 100 times faster from the parallel fraction alone ignores that the serial 40 seconds never shrinks.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A report compares a 2 ms CPU request against a 0.1 ms kernel and claims 20 times faster. Identify the missing observations.

**Trap to avoid:** Timing the kernel with a host clock and no synchronization records only the asynchronous launch call, inflating the claimed speedup further.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What changes if the input contains zero pixels?

**Trap to avoid:** Computing a grid of ceil(0 / 256) blocks and launching anyway yields a zero-sized grid, which the runtime rejects as an invalid configuration.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Would you accelerate a chain of 1,000 dependent HTTP requests using a CUDA kernel?

**Trap to avoid:** Launching 1,000 GPU threads, one per request, ignores that request k cannot start until request k minus one returns.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **More GPU cores imply every program becomes faster.** Cores only help the fraction of time spent on independent work. In worked example 1 the 20 seconds of parsing and 4 seconds of transfers stay put, so a tenfold kernel gives only a 3.125 times application speedup. A dependent chain, such as a running balance, cannot use extra cores at all.

## Self-check, retrieval and transfer

1. If parsing in worked example 1 grew to 40 seconds while the transform stayed 80 seconds, what would cap the speedup?
2. Why does batching 1,000 tiny requests change the verdict of worked example 2?
3. Name one workload in your own projects that has a dependency chain.

Short answers are in the [separate explanations](../solutions/cuda-001_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-001: What a GPU accelerates, and what it cannot make fast.
Read courses/cuda/cpp/guides/cuda-001.md and courses/cuda/cpp/lessons/cuda-001.md.
Direct prerequisites: None within this subject. Basic loops and arrays help; revisit Python or C++ foundations when needed.
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-001_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-001_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
