# cuda-088: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute serial time

Sum stage times.

**Approach.** Add the stage times for a serial pipeline: 6 ms of preparation plus 4 ms of compute gives 10 ms per batch.

**Why it is correct here.** In a serial loop the GPU waits while the CPU prepares the next batch, and the CPU waits while the GPU computes, so per-batch time is the sum of both stages.

**A plausible wrong approach.** Reporting the 4 ms GPU compute time as the step time ignores the 6 ms the GPU spends idle waiting for input.

**How to verify.** The reference asserts `serial == 10`. On a real system, time the loop with the device synchronized at each step and compare with the sum.

## Exercise 2: Compute an ideal bottleneck bound

The slowest stage limits steady state.

**Approach.** Bound ideal overlapped throughput by the slowest stage: `max(6, 4) = 6` ms per batch in steady state after the first batch fills the pipeline.

**Why it is correct here.** With prefetching, preparation of batch `k+1` overlaps compute of batch `k`. The GPU still waits 2 ms each batch because preparation is slower, so the bound is 6 ms, not 4.

**A plausible wrong approach.** Claiming overlap reduces the step to 4 ms assumes the input stage becomes free. Only a faster or more parallel preparation stage can move the bound below 6 ms.

**How to verify.** The reference asserts `ideal == 6`. A trace of an overlapped run should show GPU idle gaps of about 2 ms per batch.

## Exercise 3: Budget the queue

Multiply batch payload by queue depth.

**Approach.** Budget the prefetch queue: three batches of 8 MiB need `3*8*1024*1024 = 25165824` bytes for payloads alone.

**Why it is correct here.** Each queued batch holds its own tensors until consumed. Decoder buffers, pinned staging copies and framework overhead come on top of this floor.

**A plausible wrong approach.** Budgeting one batch because only one is used at a time ignores that all queued batches are resident at once.

**How to verify.** The reference asserts the byte count. Watch host memory while increasing queue depth and confirm growth of roughly 8 MiB per extra batch.

## Exercise 4: Explain pinned versus ordinary host storage

Pinning affects transfer behavior and host resources.

**Approach.** Explain pinned host memory: page-locked buffers allow asynchronous DMA transfers with `non_blocking=True`, while ordinary pageable memory is staged through a driver buffer before copying.

**Why it is correct here.** Pinning enables overlap of copy and compute and usually faster transfers, but pinned pages cannot be swapped, so pinning too much reduces memory available to the operating system.

**A plausible wrong approach.** Pinning every buffer by default can starve the host and slow the whole machine.

**How to verify.** Compare a transfer from a pinned tensor with one from a pageable tensor in a profiler trace, and record pinned memory totals.

## Exercise 5: Compare resident-data diagnostic

It isolates input cost without proving production throughput.

**Approach.** Run a diagnostic with a batch already resident on the GPU, repeating the compute step with no input pipeline, to measure the compute-only step time.

**Why it is correct here.** If the resident-data step is much faster than the full pipeline, input preparation is the bottleneck. The diagnostic isolates one cause.

**A plausible wrong approach.** Reporting the resident-data speed as production throughput ignores that real training must load new data every step.

**How to verify.** Report the resident and full-pipeline times side by side, labeled as a diagnostic and a production estimate.

## Exercise 6: Choose bounded worker experiments

Vary one worker or queue setting at a time.

**Approach.** Vary one loader setting at a time, such as worker count from 1 to 2 to 4 with a fixed queue depth, and stop at an explicit upper bound.

**Why it is correct here.** Changing workers and queue depth together makes it impossible to attribute an improvement. Each extra worker also costs CPU memory and process startup.

**A plausible wrong approach.** Raising all settings to their maximum at once may exhaust host memory or CPU cores and still hide which change helped.

**How to verify.** Record step time and host memory for each setting. The best setting should be confirmed by repeating it.

## Reference observation

Serial 10 ms, ideal steady-state 6 ms, queued payload 25165824 bytes.

The reference file is `courses/cuda/python/references/cuda-088_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
