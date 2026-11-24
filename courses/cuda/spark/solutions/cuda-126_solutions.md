# cuda-126: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Classify failure layers

Use first evidence rather than guessing.

**Approach.** Classify the failure layer from the first evidence: a device out-of-memory error while JVM heap is below its limit places the failure in GPU memory, not the JVM.

**Why it is correct here.** The first error message names the allocator that failed. Later errors are often consequences, such as lost executors or retried tasks.

**A plausible wrong approach.** Increasing JVM heap after a device OOM changes an unrelated limit and leaves the GPU live set unchanged.

**How to verify.** Find the earliest error in executor logs and record which layer it names before changing any setting.

## Exercise 2: Correlate job identities

Link app executor stage task and SQL IDs.

**Approach.** Correlate job identities: link the application ID, executor ID, stage ID, task attempt and SQL execution ID for the failing task.

**Why it is correct here.** These IDs connect logs, metrics and plans. Without them, evidence from different sources may describe different tasks.

**A plausible wrong approach.** Matching logs by timestamp alone can mix events from concurrent tasks. Clock differences between hosts make timestamp matching even less reliable across executors.

**How to verify.** Use the IDs from the Spark UI to find the matching executor log lines and SQL plan. Record the chain of IDs in the incident notes so the correlation can be checked later.

## Exercise 3: Budget before changing settings

Count actual live and spill categories.

**Approach.** Budget before changing settings: count the actual live-set and spill categories from metrics, then choose a change such as lower concurrency or smaller batches.

**Why it is correct here.** A budget explains why memory ran out and predicts whether a change will fit.

**A plausible wrong approach.** Trying random settings until the job passes may hide the cause and fail again on larger data. Several simultaneous changes also make it impossible to say which one fixed the failure.

**How to verify.** Compare the predicted peak after the change with measured peak in the next run. A large mismatch means a memory category is missing from the budget and should be found before more tuning.

## Exercise 4: Analyze retry side effects

At-least-once execution can duplicate writes.

**Approach.** Analyze retry side effects: two attempts writing key-7 are 2 raw writes but 1 logical key, so retries can duplicate external effects.

**Why it is correct here.** Spark retries failed tasks, giving at-least-once execution for side effects outside its commit protocol.

**A plausible wrong approach.** Sending messages directly from tasks without idempotency produces duplicates after a retry. Speculative execution can run two attempts at once, duplicating writes even without any failure.

**How to verify.** The reference asserts `raw == 2` and `idempotent == 1`. Use idempotent keys or a transactional sink, and test with an injected retry.

## Exercise 5: Define process cleanup

Terminate only owned job processes.

**Approach.** Define process cleanup that terminates only the job's own processes and pods, identified by recorded IDs or labels.

**Why it is correct here.** Owned cleanup prevents harming other jobs on shared hosts. Orphaned executor processes holding GPU memory are a common cause of the next job failing, so cleanup also protects later runs.

**A plausible wrong approach.** Killing all Java or Python processes on a node stops unrelated work. It can also kill the node's own agents, which are often Java or Python processes.

**How to verify.** List the job's processes before cleanup and confirm only those exited. Afterward, check that device memory on the GPU returned to its idle level.

## Exercise 6: Preserve an incident packet

Keep sanitized config plans logs metrics and input identity.

**Approach.** Preserve an incident packet with sanitized configuration, plans, logs, metrics and the identity of the input data.

**Why it is correct here.** The packet lets someone reproduce and analyze the failure later without access to the live system. Logs and metrics often expire on a retention schedule, so the packet may be the only lasting copy.

**A plausible wrong approach.** Keeping raw configuration with credentials risks leaking secrets. Dropping configuration entirely, on the other hand, removes the settings needed to reproduce the failure.

**How to verify.** Check the packet for secrets and confirm it contains each listed item. Record the input data identity as a path and version or checksum rather than copying sensitive data.

## Reference observation

Two attempts can target one logical output key.

The reference file is `courses/cuda/spark/references/cuda-126_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
