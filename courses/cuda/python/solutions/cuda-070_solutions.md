# cuda-070: explained solutions

Compare with your [worksheet](../lessons/cuda-070.md) attempt.

## Exercise 1: Compute live and reserved totals

Free pool blocks are reserved but not live.

**Approach.** Track two counters: reserved bytes held by the pool and live bytes owned by arrays. After the array is released, live drops to 0 and reserved stays at 1024.

**Why it is correct here.** A memory pool keeps freed blocks to serve later requests without asking the driver again. The reference asserts `live == 0 and reserved == 1024` after the release.

**A plausible wrong approach.** Reading the device memory report and concluding there is a 1024-byte leak confuses reserved with live. The block is free in the pool and will be reused.

**How to verify.** Run the cuda-070 reference and check the first assertion. With CuPy on a device, `pool.used_bytes()` and `pool.total_bytes()` would show the same split.

## Exercise 2: Reuse a free block

Equal-sized reuse need not grow reserve.

**Approach.** Request a new 1024-byte array after the release and observe that the pool hands back the free block, so live returns to 1024 and reserved stays 1024.

**Why it is correct here.** The request size matches the free block exactly. The reference asserts `live <= reserved` after reuse, which holds because no new reservation was needed.

**A plausible wrong approach.** Expecting reserved to rise to 2048 after the second allocation assumes the pool never reuses blocks. That would make every loop iteration look like growth.

**How to verify.** Model the allocate, release, allocate sequence and confirm reserved never exceeds 1024. On a device, repeat the cycle a few times and check that total pool bytes stay flat.

## Exercise 3: Diagnose a retained-output list

Drop unneeded owners and detached summaries.

**Approach.** Find the list that appends each step's output and replace it with a detached scalar summary, or drop the reference when the step ends.

**Why it is correct here.** Worked example 2 keeps four 1024-byte results live, so live bytes are 4096 and keep growing. Pool reuse cannot help because none of those arrays is ever freed.

**A plausible wrong approach.** Calling the pool's free-all function every step does not release arrays still referenced by the list. Live bytes stay at 4096 and the clearing just costs time.

**How to verify.** The reference asserts `sum(retained) == 4096` for four steps. After the fix, record live bytes for steps 1 to 4 and confirm they stay at 1024.

## Exercise 4: Explain why cache clearing is insufficient

Live objects still require storage.

**Approach.** Explain that clearing a cache returns only free blocks to the driver; arrays that are still referenced keep their storage no matter how often the cache is cleared.

**Why it is correct here.** In the retained-list case all 4096 bytes are live. Clearing the cache may reduce reserved bytes in the healthy case of worked example 1 but cannot touch live bytes.

**A plausible wrong approach.** Adding `free_all_blocks()` after every step makes the memory report drop slightly while the actual leak continues, giving false confidence.

**How to verify.** Compare live bytes before and after clearing in the retained-output model; they must be equal. The fix that changes live bytes is dropping references.

## Exercise 5: Design bounded snapshots

Record before and after fixed small steps.

**Approach.** Take a memory snapshot before and after a fixed small number of steps, such as four, each with the same input size, and compare live and reserved separately.

**Why it is correct here.** A bounded loop with a fixed size shows the pattern: healthy reuse keeps live at one result, retention grows by one result per step, exactly 1024 bytes in this chapter's model.

**A plausible wrong approach.** Running until the device runs out of memory and reading the error message is unbounded and can disturb other users of a shared device.

**How to verify.** Record four snapshots; growth of 1024 live bytes per step identifies retention, flat live with flat reserved identifies reuse.

## Exercise 6: Separate host RAM and VRAM

Container host-memory limits do not generally cap VRAM.

**Approach.** Separate host RAM limits from device memory: a container memory limit constrains host allocations, while VRAM is managed by the GPU driver.

**Why it is correct here.** The pool in this chapter manages device memory. A container that limits RAM to 4 GB does not, in general, stop a process from reserving device memory.

**A plausible wrong approach.** Setting a container memory limit and expecting it to prevent device out-of-memory errors gives no protection. The device can still fill up.

**How to verify.** List which tool reports each: host RSS from the OS, device usage from the GPU driver or the library pool. A correct note names both separately.

## Self-check answers

1. **What does a stable reserved total across repeated equal workloads usually mean?** The pool is reusing its cached blocks. That is normal behavior, not a leak, as long as live bytes also return to the same level after each step.

2. **Which signal suggests retained tensors, outputs or graphs?** Live allocations that grow after every step of an equal workload, like the list of results that reaches 4096 bytes after four steps.

3. **Why is clearing the cache not a repair for a workload whose live set exceeds memory?** Cache clearing returns only free blocks to the driver. Arrays the model still needs remain live, so the required memory is unchanged.

## Reference observation

Live 1024, reserved 1024, retained-output example 4096 bytes.

Asserted by `courses/cuda/python/references/cuda-070_cpu.py`.
