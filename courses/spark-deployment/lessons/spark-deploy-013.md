# spark-deploy-013: Observe controlled worker loss and recovery

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-011`, `spark-deploy-012`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Lose an owned worker during useful work

An executor failure can cause Spark to retry a task or recompute unavailable data. This is not the same as restarting a failed driver or recovering an external sink. A successful retry must preserve the original input population and output contract. Numerical success after silently dropping a partition is not recovery.

The workshop wrapper can stop only one of its two named workers after validating container ownership. The host controls the failure; services have no Docker socket. The deterministic partition delay holds work long enough to observe a running stage. Sleeping is only a fault-injection aid, not a method for proving that a particular task has started.

## Key terms

- **Executor loss:** The disappearance of an executor, here caused by stopping an owned worker container during a running stage.
- **Task retry:** A new attempt of a failed task on a surviving executor, recorded with a new attempt number.
- **Partition coverage:** The check that the final partition results include every input ID exactly once after recovery.
- **Fault injection:** A deliberate failure, such as stopping worker-a after observing its running task, used to test recovery.
- **Idempotency key:** A durable identifier that prevents a retried task from duplicating an external effect.

## Worked case A: observe, stop and verify recovery

In terminal one:

```sh
python3 lab.py submit --partition-seconds 15 --allow-one-worker
```

In terminal two, first inspect the live UI and confirm an active task on worker-a, then:

```sh
python3 lab.py worker-stop worker-a
```

The `--allow-one-worker` flag permits final results from the survivor and does not waive count, partition or moment oracles. Record the actual application ID, stage/task/attempt, worker container ID, stop timestamp and executor-lost diagnostic. The final eight partition records must still cover all IDs exactly once and recover intercept 3/slope 2. If the stop occurred after work completed, the run did not test in-flight recovery.

The application report intentionally writes `worker_loss_observed: false`: the driver cannot certify the host's intervention merely because one worker returned results. An acceptance collector must combine the host action and Spark events before claiming recovery. Do not flip that field by hand and call it measured evidence.

## Worked case B: restore capacity without replacing data

```sh
python3 lab.py worker-start worker-a
python3 lab.py submit
```

The new baseline must again show both worker hosts and two executor registrations. It is a new application with a new ID. Compare its numerical oracles to the earlier baseline, while preserving the failed/retried application's events separately. Do not delete event logs to make the recovered run appear clean.

## Observed local qualification

The retained ARM64 run stopped worker-a only after observing its RUNNING task. Partition 0 then completed as attempt 1 on worker-b; all eight successful partition results preserved 100000 rows and the same coefficients and future-input predictions. The host action and task evidence are bound in the project receipt. A later restored baseline used both workers again. This observed stop/retry is narrower than physical-host or driver-loss recovery.

## Worked example: reconciling task attempts after worker-a is stopped

```python
N, PARTS = 100000, 8


def summary(p):
    lo, hi = p * N // PARTS, (p + 1) * N // PARTS
    return {"partition": p, "rows": hi - lo, "sx": sum(range(lo, hi))}


attempts = [
    dict(summary(p), attempt=0, host="worker-a" if p % 2 == 0 else "worker-b", ok=True)
    for p in range(PARTS)
]
attempts[0]["ok"] = False
attempts.append(dict(summary(0), attempt=1, host="worker-b", ok=True))

naive_rows = sum(a["rows"] for a in attempts)
accepted = {a["partition"]: a for a in attempts if a["ok"]}
rows = sum(a["rows"] for a in accepted.values())
sx = sum(a["sx"] for a in accepted.values())
print("attempt records:", len(attempts), "naive row total:", naive_rows)
print("accepted partitions:", sorted(accepted), "rows:", rows, "sx:", sx)
print("partition 0 finished on", accepted[0]["host"], "attempt", accepted[0]["attempt"])
print("coverage ok:", sorted(accepted) == list(range(PARTS)) and rows == N and sx == 4999950000)
```

Output from running the block above:

```text
attempt records: 9 naive row total: 112500
accepted partitions: [0, 1, 2, 3, 4, 5, 6, 7] rows: 100000 sx: 4999950000
partition 0 finished on worker-b attempt 1
coverage ok: True
```

The simulation recreates the observed qualification run in miniature. `spark.range(0, 100000, numPartitions=8)` gives each partition 12500 consecutive IDs, and partition 0's first attempt on worker-a is marked failed while attempt 1 completes on worker-b. Summing every attempt record, as a naive log scraper would, reports 112500 rows. Keeping exactly one successful attempt per partition restores 100000 rows and the exact `sx` of 4999950000, covering partitions 0 through 7 once each, which is the oracle the chapter requires before calling the run recovered. The partition summaries are computed in plain Python rather than by Spark, so they reproduce the bookkeeping, not the scheduler. In the real report, the attempt number comes from `TaskContext.attemptNumber()` and the host from the executor, and those fields must still be joined to the host-side stop timestamp, which is why the application keeps `worker_loss_observed` false instead of inferring recovery from the survivor alone.

## Worked example: why a retried side effect needs an idempotency key

```python
def run_partition(sink, partition, attempt, keyed):
    record = {"partition": partition, "event": "fit-report-ready"}
    if keyed:
        sink.setdefault(f"app-0004/partition-{partition}", record)
    else:
        sink.setdefault("log", []).append(dict(record, attempt=attempt))
    if attempt == 0 and partition == 0:
        raise ConnectionError("executor lost after the side effect")


for keyed in (False, True):
    sink = {}
    for partition in range(8):
        for attempt in range(2):
            try:
                run_partition(sink, partition, attempt, keyed)
                break
            except ConnectionError:
                continue
    size = len(sink) if keyed else len(sink["log"])
    print(f"keyed={keyed}: {size} sink records for 8 partitions")
```

Output from running the block above:

```text
keyed=False: 9 sink records for 8 partitions
keyed=True: 8 sink records for 8 partitions
```

A task that sends a notification and then loses its executor will run again, and the second attempt repeats the effect. The function models that: partition 0's first attempt writes to the sink and then raises, and the retry loop runs it again. With an append-only log the sink ends with nine records for eight partitions, one duplicate that no Spark metric would flag because the job itself succeeded. With a deterministic key built from the application and partition, the retry finds the existing record and the sink holds exactly eight. The key here is a plain dictionary entry; in a real system it must be enforced by the external store, for example a unique constraint or a conditional write, since two concurrent speculative attempts could both pass a separate existence check. A deterministic numerical summary, like this chapter's partition sums, needs none of this because replaying it yields identical values and only the accepted result is kept.

## Diagnose and transfer

A pure deterministic map can be replayed. Sending an email, charging a card or appending to an uncontrolled file inside a task can duplicate effects on retry. Use durable idempotency keys and an actual sink protocol for such work; task success alone cannot prove exactly-once external effects.

An RDD result includes successful partition results, while accumulators and side-effect logs can reflect attempts. Do not sum all observed attempt records as if they were disjoint data. A malformed input or deterministic code bug may fail every attempt; increasing retry limits will not repair it.

This single-host container-loss exercise does not establish multi-machine high availability, master recovery, storage loss recovery or GPU fault tolerance. Every independent Spark package must additionally run its own actual fit, prediction and forecast API in the required isolated topology.

## Primary references

- [Spark execution and retry settings](https://spark.apache.org/docs/4.0.1/configuration.html)
- [RDD fault recovery model](https://spark.apache.org/docs/4.0.1/rdd-programming-guide.html)
