# cuda-126: Operational diagnosis, metrics and recovery

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-120`, `cuda-122`, `cuda-125`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Classify failure layers.
- Correlate job identities.
- Budget before changing settings.
- Analyze retry side effects.
- Define process cleanup.
- Preserve an incident packet.

## Mechanism and vocabulary

GPU Spark failures can originate in query semantics, JVM integration, native library loading, device memory, host memory, spill disk, network or scheduler state. Preserve the first relevant error and correlate it with executor, task and SQL execution identity. A later generic task retry may hide the original native failure. Repeatedly increasing memory without a budget can move the problem between tiers.

Recovery should preserve input snapshots, output commit semantics and event logs. Retrying a task is safe only under the application's side-effect contract; external writes inside a UDF can be duplicated. A poisoned device context may require a fresh owned process, while device-wide reset is an administrator operation that can affect unrelated jobs. The classroom must never reset a shared GPU automatically.



### Key terms

- **First relevant error:** The earliest error tied to the failure, which later generic retries can hide.
- **Task retry:** Spark rerunning a failed task, which is safe only when the task's output commit is idempotent.
- **Event log:** Spark's recorded history of jobs, stages, tasks and SQL executions used for later diagnosis.
- **Incident packet:** A bounded bundle of logs, plans, configuration and identities that documents one failure.

## Worked examples

### Worked example 1

An executor fails with device OOM while JVM heap is below its limit. Increasing heap does not address the measured GPU live-set problem.

### Worked example 2

A task writes an external message then fails before Spark commits its output. Retrying may send the message twice unless an idempotency or transactional design handles it.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-126_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-126_cpu.py
```

```python
events = [("task1", "write", "key-7"), ("task1-retry", "write", "key-7")]
raw = len(events)
idempotent = len({key for _, _, key in events})
assert raw == 2 and idempotent == 1
print("CPU retry model:", raw, "attempts;", idempotent, "logical keys")
```

**Expected observation:** Two attempts can target one logical output key.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `raw` | `2` |
| `idempotent` | `1` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-126.md) before opening hints.

### Exercise 1: Classify failure layers

**Trap to avoid:** Increasing JVM heap after a device OOM changes an unrelated limit and leaves the GPU live set unchanged.

### Exercise 2: Correlate job identities

**Trap to avoid:** Matching logs by timestamp alone can mix events from concurrent tasks. Clock differences between hosts make timestamp matching even less reliable across executors.

### Exercise 3: Budget before changing settings

**Trap to avoid:** Trying random settings until the job passes may hide the cause and fail again on larger data. Several simultaneous changes also make it impossible to say which one fixed the failure.

### Exercise 4: Analyze retry side effects

**Trap to avoid:** Sending messages directly from tasks without idempotency produces duplicates after a retry. Speculative execution can run two attempts at once, duplicating writes even without any failure.

### Exercise 5: Define process cleanup

**Trap to avoid:** Killing all Java or Python processes on a node stops unrelated work. It can also kill the node's own agents, which are often Java or Python processes.

### Exercise 6: Preserve an incident packet

**Trap to avoid:** Keeping raw configuration with credentials risks leaking secrets. Dropping configuration entirely, on the other hand, removes the settings needed to reproduce the failure.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Find the first error in the logs and decide which layer produced it, before reading any later retries.
2. Link the application, executor, stage, task and SQL execution identifiers that belong to the same failure.
3. Count the actual live set and spill categories before changing any memory setting.
4. Ask what happens to an external write when the same task runs a second time.
5. List the processes your job started and stop only those, leaving any shared device untouched.
6. Gather sanitized configuration, plans, logs, metrics and the input identity into one packet.

## Common mistakes and self-check

A common mistake is raising memory settings until an error disappears. A device out-of-memory error with JVM heap below its limit is a GPU live-set problem, so more heap changes nothing, and unbudgeted increases only move pressure between tiers. Another is resetting a shared GPU to recover, which can break unrelated jobs. Fix both by preserving the first relevant error, correlating it with executor, task and SQL identities, budgeting each memory category and stopping only processes the job owns. Treat retries as at-least-once execution, so external writes need idempotency.

**Misconception:** Raising the task retry count makes a failing GPU job more reliable. **Correction:** Retries help with transient faults such as a lost executor, but a deterministic failure, like a device out-of-memory error on the same skewed partition or a native library mismatch, fails the same way on every attempt. Extra retries then delay the report, repeat external side effects and can bury the first error under many copies. Classify the failure first; retry only transient causes, and fix deterministic ones by changing the data split, memory budget or environment.

**Evidence limit:** The reference shows two attempts targeting one logical output key. It does not produce real failures, so native library errors, device context poisoning and recovery behavior must be studied from preserved logs of an owned job, never by causing failures on shared hardware.

1. Why preserve the first relevant error?
2. Why can task retries duplicate side effects?
3. Who may reset a device?

Answers: [self-check answers](../solutions/cuda-126_solutions.md#self-check-answers).

## Primary references

- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-126: Operational diagnosis, metrics and recovery.
Read courses/cuda/spark/guides/cuda-126.md and courses/cuda/spark/lessons/cuda-126.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
