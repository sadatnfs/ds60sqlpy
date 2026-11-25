# cuda-060: Multiple GPUs, topology and collective communication

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-028`, `cuda-039`, `cuda-040`, `cuda-044`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Verify a multi-GPU all-reduce result, record the observed topology and interpret strong or weak scaling.

**Scope:** Device selection, separate contexts/address spaces, peer access, PCIe/NVLink topology, decomposition, halo exchange, collectives and failure propagation.

**Evidence to produce:** Correct combined result, observed topology, collective completion and strong/weak scaling interpretation where meaningful.

## Purpose, vocabulary and mental model

Multiple GPUs have distinct allocations, execution contexts and communication paths. Peer access may be available for a pair, but it must be supported and explicitly configured under the platform's rules. Topology affects whether traffic uses PCIe, NVLink or other paths. A collective such as all-reduce combines values and makes the result available to every participant. Participants must agree on communicator, datatype, count and collective order; mismatches can hang or fail. Multi-GPU within one machine does not prove multi-node operation, which adds network, process-launch and failure concerns.

### Key terms

- **All-reduce:** A collective that combines values from every participant and returns the same result to all of them.
- **NCCL communicator:** An object that describes the participating GPUs and their ranks for NCCL collectives.
- **Peer access:** The ability of one GPU to read or write another GPU's memory directly over NVLink or PCIe.
- **Strong scaling:** Speedup for a fixed total problem size as the number of GPUs grows.
- **Weak scaling:** Efficiency when the problem size grows in proportion to the number of GPUs.

## Mathematical contract

\[
E_p=\frac{S_p}{p}
\]

Strong-scaling efficiency E uses speedup S for fixed total work on p devices with the same result and timing scope.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-060_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-060_cpu.py
```

## Worked example 1: trace the mechanism

Split \([1,2,3,4,5]\) across two devices as \([1,2,3]\) and \([4,5]\). Local sums are six and nine; a combined sum is fifteen. A gather gives the final result to one destination, whereas all-reduce gives fifteen to both participants. A CPU partition model demonstrates semantics only.

**Why:** Local sums 6 and 9 add to 15, and all-reduce delivers 15 to both devices.

```python
values = [1, 2, 3, 4, 5]
partials = [sum(values[:3]), sum(values[3:])]
all_reduce_model = [sum(partials)] * 2
assert partials == [6, 9] and all_reduce_model == [15, 15]
print({"CPU_collective_model": all_reduce_model, "multi_GPU_executed": False})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'CPU_collective_model': [15, 15], 'multi_GPU_executed': False}
```

**Check:** The reference asserts partials == [6, 9] and all_reduce_model == [15, 15], and prints multi_GPU_executed False.

## Worked example 2: change a meaningful condition

For a radius-one stencil split into left and right partitions, each side needs its neighbor's boundary value before updating edge cells. Exchange halos and establish completion before reading them. Copying only the interior or assuming all device pointers share one pool breaks the contract.

**Why:** A radius-one stencil at the partition edge needs the neighbor's adjacent value.

**Check:** Compare the split result against a single-array stencil on the same input.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Split [1, 2, 3, 4, 5] into [1, 2, 3] and [4, 5], sum each locally, then combine.

**Trap to avoid:** Using a gather when every device needs the total leaves the second device without the result.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Exchange one boundary value each way before updating edge cells, and wait for the exchange to complete.

**Trap to avoid:** Updating edges before halos arrive uses stale or missing neighbor values.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute strong-scaling efficiency for speedup 1.6 on two GPUs.

**Trap to avoid:** Comparing runs with different problem sizes makes the ratio meaningless for strong scaling.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Rank zero calls all-reduce while rank one calls broadcast first. Diagnose it.

**Trap to avoid:** Adding sleeps does not fix mismatched collectives and can still hang.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What can one GPU prove about two-device peer access?

**Trap to avoid:** Claiming peer behavior from one GPU reports evidence that was never collected.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Define weak versus strong scaling.

**Trap to avoid:** Reporting weak-scaling results as strong-scaling speedup overstates gains.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Two GPUs share memory automatically or multi-GPU execution proves multi-node readiness.** Each GPU has its own memory and context, and peer access must be supported and enabled per pair. Multi-node work adds networking, process launch and failure handling that a single machine never tests. State which topology was actually used for every claim.

## Self-check, retrieval and transfer

1. What is strong-scaling efficiency for speedup 1.6 on two GPUs?
2. Rank zero calls all-reduce while rank one calls broadcast. What happens?
3. What does all-reduce give in worked example 1 that a gather does not?

Short answers are in the [separate explanations](../solutions/cuda-060_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [Multi-GPU programming](https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/multi-gpu-systems.html)
- [NCCL](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-060: Multiple GPUs, topology and collective communication.
Read courses/cuda/cpp/guides/cuda-060.md and courses/cuda/cpp/lessons/cuda-060.md.
Direct prerequisites: `cuda-028`, `cuda-039`, `cuda-040`, `cuda-044`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-060_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-060_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
