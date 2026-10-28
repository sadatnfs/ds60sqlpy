# apache-025: Failure, retry and retained evidence

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-021`, `apache-008`, `apache-006`.

## Recovery must name the state it preserves

A scheduler coordinates work, an executor performs tasks, and storage retains
source or intermediate bytes according to its own contract. Restarting one of
these processes does not automatically recover every other state category. A
client can retain a query receipt even when the scheduler forgets the job, or a
scheduler can remember a task whose intermediate files were lost.

The small workshop uses the released Python scheduler wrapper's default state
backend. It does not promise durable scheduler job history across process restart.
Its canonical fixture and completed evidence receipts live in an independent owned
volume. The failure check reports these categories separately and does not replay
a job merely because its last outcome is unknown.

Fault injection is an explicit project action, not a classroom pad operation.
Only the known child process of this owned workshop is stopped. The command must
verify process identity and avoid matching arbitrary host names or using broad
kill expressions. A one-container process topology can teach a real executor
failure while remaining distinct from a lost machine or network partition.

## Worked case A: remove the only executor from a bounded cluster

The project first executes and records a successful query. It then stops the
owned executor process, waits for its exit and submits a fresh bounded query
without execution capacity. The client must report a bounded failure and retain
its failed or unknown outcome. It is reaped before capacity is restored.
The report records that one executor was absent and whether the new query
failed or exceeded its deadline.

This experiment does not guarantee transparent recovery of an in-flight task.
The timing and workload are too small to ensure a selected task was running on
the stopped executor. An in-flight recovery claim would require identifying that
task, interrupting it after its start and observing its actual retry or failure.
The lesson intentionally avoids presenting a new successful query as evidence
that an earlier interrupted computation recovered.

After the observation, the project explicitly restarts the owned scheduler and
executor, discarding the unknown job from this default non-durable scheduler
state. It checks readiness before a separately identified fresh request. A process that exists but has not registered
with the scheduler is not yet useful capacity. Readiness combines known process
identity, listening endpoints and an actual successful bounded query.

## Worked case B: restart the scheduler without inventing job continuity

The scheduler restart check captures completed receipts and canonical source
identity, stops the known scheduler, restarts it and waits for actual readiness.
It then inspects the retained receipt without executing that receipt again.
Only a separately identified fresh query is submitted to prove the restarted
installation can perform new work.

If the default scheduler loses previous job history, the report states that
limitation. A retained JSON receipt is application evidence, not a recovered
scheduler execution graph. Likewise, surviving fixture bytes do not prove that
old shuffle files are valid or that another client can resume a half-consumed
result stream.

A real production recovery design must select and qualify durable scheduler state,
executor registration, intermediate storage, timeouts, retries and output commit
semantics together. An external sink needs its own idempotence or transaction
boundary. An engine retry can otherwise repeat a side effect even while producing
one final query result.

## Mistakes, diagnosis and interview discussion

Keep the fault timestamp, affected process identity, query identity, observed error
category and retained source/result identities. Bound waits and preserve ambiguous
outcomes instead of reporting success after any process comes back. Distinguish
service availability during interruption from persistence after recovery: a
single scheduler can retain data while being unavailable during its restart.

**Interview discussion: what is missing from the statement the cluster recovered?**
It must specify which request, source version, state, output and service capacity
were restored, and whether records were lost, duplicated or unavailable during
the event. These two cases observe real owned process failures while refusing to
infer in-flight retry, durable scheduler history or multi-host availability from
a successful later query.

The [complete Ballista workshop](../projects/ballista/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Explicit owned fault experiments

Run only in the copied workshop with its canonical fixture and known ownership.

```bash
bash run.sh check
bash run.sh failure-check
bash run.sh evidence
```

The report distinguishes one-slot fresh-query behavior, scheduler restart,
retained source/receipts and a separately identified new request. It does not
silently rerun an old receipt or claim recovery of an unidentified in-flight task.

For whole-container lifecycle:

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
```

Consult QUALIFICATION for the exact observed failure result on the native platform.

## Primary references

- [Ballista scheduler](https://datafusion.apache.org/ballista/user-guide/scheduler.html)
- [Ballista architecture](https://datafusion.apache.org/ballista/contributors-guide/architecture.html)
