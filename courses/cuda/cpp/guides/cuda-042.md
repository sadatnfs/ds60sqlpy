# cuda-042: Unified memory, residency and migration

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`, `cuda-032`, `cuda-039`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Report unified memory behavior tied to queried device capabilities and observed page migration.

**Scope:** Unified virtual addressing versus managed allocation, residency, migration, first touch, prefetch and oversubscription.

**Evidence to produce:** Correctness and a report tied to actual memory capabilities and observed movement.

## Purpose, vocabulary and mental model

Unified virtual addressing concerns address-space organization; managed memory provides an allocation model whose residency and migration are managed under supported platform rules. Neither term promises uniform access cost. First touch can trigger movement, alternating host/device access can cause repeated migration, and prefetch is a placement hint with its own ordering requirements. Coherent systems, discrete GPUs and WSL can have different capabilities. Query support and use the selected platform's documented contract. A single pointer does not erase the need to reason about which processor owns useful work at each phase.

### Key terms

- **Managed memory:** An allocation from `cudaMallocManaged` that both host and device can address through one pointer.
- **Page migration:** Moving memory pages between host and device on demand, which costs time the first time each page is touched.
- **Prefetch:** A `cudaMemPrefetchAsync` hint that moves pages to a processor before they are needed.
- **Unified virtual addressing:** One virtual address space shared by host and devices so a pointer value identifies its memory.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-042_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-042_cpu.py
```

## Worked example 1: trace the mechanism

A 64 MiB managed array is initialized by the CPU and then processed repeatedly on a GPU. The first GPU pass may include migration costs that later resident passes do not. Report the first pass separately rather than using a warm result to promise cold-start latency.

**Why:** The first pass may fault and migrate pages to the device, which later resident passes avoid.

```python
mib, transitions = 64, 20
modeled_moved_mib = mib * transitions
assert modeled_moved_mib == 1280
print({"simplified_transition_volume_MiB": modeled_moved_mib, "actual_migration_measured": False})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'simplified_transition_volume_MiB': 1280, 'actual_migration_measured': False}
```

**Check:** Record first and steady-state times separately on a GPU and label which pass each number describes.

## Worked example 2: change a meaningful condition

Alternating a full CPU pass and full GPU pass for ten rounds can move the working set repeatedly. A simplified model counts twenty ownership transitions, unlike a batched design with one transfer to each side. Actual migration can occur at finer granularity and depends on platform support.

**Why:** Ten alternating rounds model twenty transitions of 64 MiB, or 1,280 MiB of potential movement.

**Check:** The reference asserts modeled_moved_mib == 1280 and marks actual_migration_measured False.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Time the first GPU pass over the CPU-initialized 64 MiB managed array separately from later passes.

**Trap to avoid:** Reporting only a warm pass as the speed of managed memory hides the first-touch migration a user pays.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Batch CPU and GPU passes so data changes owner once per side instead of every round.

**Trap to avoid:** Assuming a single pointer means no data moves ignores that pages follow whichever processor touches them.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Distinguish a pointer value from physical residency.

**Trap to avoid:** Reading the pointer value to decide whether data is on the GPU treats an address as a location.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can managed memory still run out of usable resources?

**Trap to avoid:** Allocating more managed memory than the device holds and assuming it just works can thrash or fail.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an unsupported prefetch capability do?

**Trap to avoid:** Ignoring the returned error and timing as if prefetch happened credits a nonexistent optimization.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Redesign an alternating pipeline to reduce movement.

**Trap to avoid:** Adding prefetch calls inside the alternating loop still moves the data every round.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **One pointer means one physically uniform memory pool or that managed allocation eliminates data-movement cost.** A single pointer hides where the data currently lives. Managed memory still moves pages between host and device, so first touch, alternating access and oversubscription cost real transfers, as worked example 2 shows with twenty transitions. Prefetching and batching each side's work reduce that movement, but only measurement on the target platform confirms the saving. In worked example 2, ten alternating rounds cause twenty ownership transitions, while batching all CPU work and then all GPU work needs only one transfer to each side.

## Self-check, retrieval and transfer

1. Why report the first GPU pass of worked example 1 separately?
2. What does unified virtual addressing promise?
3. What is prefetch?

Short answers are in the [separate explanations](../solutions/cuda-042_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [Unified memory](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/unified-memory.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-042: Unified memory, residency and migration.
Read courses/cuda/cpp/guides/cuda-042.md and courses/cuda/cpp/lessons/cuda-042.md.
Direct prerequisites: `cuda-005`, `cuda-032`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-042_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-042_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
