# cuda-105: explained solutions

Compare with your [worksheet](../lessons/cuda-105.md) attempt.

## Exercise 1: Compute barrier time

The slowest rank controls the barrier.

**Approach.** With ranks taking 10, 12 and 30 ms before a barrier, the compute phase takes at least `max(10, 12, 30) = 30` ms, not the mean of about 17.3 ms.

**Why it is correct here.** A barrier releases only when every rank arrives. The two fast ranks spend 20 and 18 ms waiting, so the slowest rank sets the step time.

**A plausible wrong approach.** Reporting the average rank time predicts 17.3 ms and hides 13 ms of idle time per step, which makes adding ranks look more efficient than it is.

**How to verify.** The reference asserts `max(rank_ms) == 30`. In a real trace, compare the per-rank time spent waiting in the collective with the gap to the slowest rank.

## Exercise 2: Compare parallelism types

Separate model replication and operation/layer/state partition.

**Approach.** Compare data parallelism, which replicates the model and splits examples, with tensor, pipeline and sharded-state parallelism, which partition operations, layers or optimizer state.

**Why it is correct here.** Data parallelism needs the whole model on each device and communicates gradients. Partitioning methods fit larger models but add communication inside the forward and backward passes.

**A plausible wrong approach.** Using data parallelism for a model that does not fit on one device fails immediately, because each replica needs all parameters, gradients and optimizer state.

**How to verify.** For each method write down what is replicated, what is partitioned and what is communicated per step, then check the per-device memory against device capacity.

## Exercise 3: Diagnose a missing rank

Bound waits and stop the owned job.

**Approach.** Diagnose a missing rank by bounding waits: a collective timeout turns a hang into an error that names the operation, after which the launcher stops all owned processes.

**Why it is correct here.** Without a bound, ranks that reached the collective wait forever for a rank that crashed or never started, and no error reaches anyone.

**A plausible wrong approach.** Restarting only the missing rank while the others wait in a collective fails, because the new process does not join the existing communicator state.

**How to verify.** Simulate the failure by delaying one rank past the timeout in a small job and confirm every rank exits with an error inside the configured bound.

## Exercise 4: Define checkpoint consistency

Use a documented common update boundary.

**Approach.** Define checkpoint consistency as every rank saving at the same completed update step; a checkpoint with rank 0 at step 10 and rank 1 at step 11 is rejected.

**Why it is correct here.** Ranks share parameters or hold partitions of the same model. Mixing steps combines states that never coexisted, so resuming does not continue any real training run.

**A plausible wrong approach.** Accepting each rank's latest file independently produces mixed-step checkpoints whenever a failure occurs during saving.

**How to verify.** The reference computes `consistent = len(set(steps.values())) == 1` and asserts it is false. Store the step in each shard and check equality before loading.

## Exercise 5: Budget communication

Count bytes and frequency per collective.

**Approach.** Budget communication by counting bytes and frequency for each collective, such as an all-reduce of gradient bytes once per step for data parallelism.

**Why it is correct here.** Communication time depends on the bytes moved and link bandwidth, so the byte count per step shows whether the network can keep up with compute.

**A plausible wrong approach.** Estimating communication from the parameter count without element size or frequency misses that float32 gradients are four bytes and some collectives run several times per step.

**How to verify.** Compute bytes per step from parameter count and dtype, then compare against bytes recorded by the communication library's logging for one step.

## Exercise 6: Design owned-host cleanup

Terminate only declared job resources and preserve checkpoints.

**Approach.** Design owned-host cleanup: on failure, terminate only processes and resources the job created, recorded by process IDs or job labels, and keep completed checkpoints.

**Why it is correct here.** Shared hosts run other jobs. Ownership records make cleanup safe, and keeping checkpoints allows resuming from the last consistent step.

**A plausible wrong approach.** Killing every GPU process on a host stops other users' jobs, while deleting the output directory loses valid checkpoints.

**How to verify.** List the recorded process IDs before cleanup and confirm afterward that only those exited and checkpoints remain.

## Self-check answers

1. **Why does the slowest rank set a synchronized step's time?** Every rank must reach the barrier or collective before any can continue, so the 30 ms rank sets the time even though the average is 17.3 ms.

2. **How do tensor and pipeline parallelism differ?** Tensor parallelism splits individual operations across devices; pipeline parallelism assigns different layers to different devices.

3. **Why can a browser lesson not create a cluster?** Multi-host training needs owned hosts, network access and prepared software, none of which a lesson page provides.

## Reference observation

Barrier 30 ms; mixed-step checkpoint rejected.

Asserted by `courses/cuda/python/references/cuda-105_cpu.py`.
