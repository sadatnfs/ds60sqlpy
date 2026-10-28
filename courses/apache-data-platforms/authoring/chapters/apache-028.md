## A task attempt can fail after producing a side effect

Airflow retries task instances according to their configured policy. A retry is
a new attempt at the task's work, not a rollback of every external effect from
the earlier attempt. If an attempt writes output and then loses its acknowledgement,
a later attempt must avoid creating a duplicate business action. Retry safety
belongs in the task's data and side-effect contract.

The workshop writes one deterministic partition per validated day. It creates a
complete temporary file, flushes it through the file handle and atomically replaces
the partition path. The stored record includes source identity, interval and
logical values. Repeating the same logical write yields the same intended output,
rather than appending another copy of the same daily rows.

Atomic replacement of one local file is a narrow storage boundary. It is not a
transaction across several files, a remote database and an email. A production
workflow may need a table commit, idempotent API, outbox or reconciliation process.
Airflow's success state alone cannot extend the filesystem operation into an
end-to-end distributed transaction.

## Worked case A: repeat the same partition safely

The first daily run computes a deterministic output and records its source hash.
The retry-check action reads the completed partition and compares its exact values
with the fixture oracle. Repeating the same logical work must leave one current
partition with the same semantics. The checker does not accept an increased row
count as a normal consequence of retry.

The output path is derived only from a validated day in the finite fixture.
A run identifier or caller text is never used as an arbitrary filesystem path.
Temporary names are created inside the owned output directory and only their
exact files are replaced or removed. This keeps a teaching failure from becoming
an accidental deletion of unrelated learner source or state.

A file's content identity can remain unchanged while its modification time changes.
The oracle therefore checks bytes or canonical logical fields, not only a timestamp.
For an external sink, use the sink's supported commit and idempotence mechanism
rather than transplanting local os.replace semantics to object storage.

## Worked case B: one real transient failure followed by retry

The DAG contains a task that deliberately fails its first attempt for each owned
run after recording a small attempt marker. It has one configured retry and a
short delay. On the second attempt it proceeds, and the downstream write completes.
The checker inspects actual Airflow task-instance attempt counts and final states,
not a Python loop that merely prints retry labels.

The marker is a controlled fixture mechanism to make a transient failure
reproducible. It is not a general distributed lock or a substitute for Airflow's
metadata state. The program keeps its identity tied to the actual run and verifies
that an unexpected marker does not cause unrelated work to be skipped. Retained
logs explain the intentional first failure beside the later successful attempt.

Clearing a task or triggering a new run is different from an automatic retry.
Each action has its own identity and can cause additional effects. A safe runbook
names the intended partition and effect boundary before taking the action, then
checks the result afterward. Do not delete metadata merely to make a failed task
look new or hide the reason its earlier attempt failed.

## Mistakes, diagnosis and interview discussion

Use retries for failure categories that can reasonably succeed later. A malformed
schema, unauthorized connection or invalid parameter should not be retried
indefinitely. Bound retry count and total execution time, retain the final failure
and distinguish a completed data effect from a failure to report its receipt.
Keep task logs free of credential values and bulk payloads.

**Interview discussion: does setting retries to three make a task reliable?**
It adds attempts under a policy, but the task still needs correct identity,
idempotence, timeouts, output validation and an understandable permanent-failure
path. These cases show a safe local output contract and an actual scheduled
failure/retry transition without claiming that the orchestrator rolls back
arbitrary external systems.

The [complete Airflow workshop](../../projects/airflow/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.
