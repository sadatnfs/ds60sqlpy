# Bridge Day 8 — Production capstone: observability, security, and recovery

**Level:** Advanced  
**Prerequisite:** [Bridge Day 7](day07_async_bounded_concurrency.md)

## Why this matters

Production readiness is not a framework choice. It is evidence that a program
behaves predictably on success, invalid input, partial failure, retry, restart,
and shutdown—without exposing secrets. This capstone keeps effectful adapters
small and makes orchestration order observable with fakes before any live
database run.

## Objectives

By the end, you can:

- orchestrate extractor, sink, checkpoint, metric, and logger boundaries;
- advance a checkpoint only after a durable batch write;
- resume deterministically after a partial failure;
- emit low-cardinality metrics and secret-safe logs;
- validate PostgreSQL transport requirements without exposing the URL;
- write a production-readiness and recovery checklist.

## Vocabulary

| Term | Meaning |
|---|---|
| checkpoint | Durable progress from which a job can safely resume |
| at-least-once delivery | A record may be retried, so the sink must tolerate duplicates |
| observability | Evidence from logs, metrics, and traces that explains system behavior |
| cardinality | The number of distinct metric label combinations |
| recovery point | The last durable state from which processing resumes |
| least privilege | Granting only the database permissions a job needs |
| threat model | A structured account of assets, attackers, boundaries, and mitigations |

## Run the starter

```powershell
.\.venv\Scripts\python.exe bridge\lessons\day08_production_capstone.py
```

```bash
.venv/bin/python bridge/lessons/day08_production_capstone.py
```

## Capstone scenario

Build a `JobRunner` that:

1. loads the last sequence checkpoint;
2. asks an extractor for records strictly after it;
3. validates positive, increasing sequences and unique record IDs;
4. writes records in bounded batches;
5. saves each batch's final sequence only after the sink returns successfully;
6. records safe counts and outcomes;
7. re-raises failures so the scheduler observes a failed run.

The ordering invariant is:

```text
sink.write(batch) succeeds -> checkpoint.save(last_sequence)
```

Reversing it can lose data: after a crash, the job would skip a batch that was
never durably written. Writing first can repeat a batch after an uncertain
failure, so the sink needs the idempotency design from Day 4.

## Worked example: useful, bounded telemetry

Good metric dimensions are stable and few:

```text
records_read{job="sales"}
records_written{job="sales"}
job_failures{job="sales", error_type="OperationalError"}
```

Do not use record IDs, customer IDs, raw exceptions, URLs, or payload fields as
metric labels. They create high cardinality or leak sensitive data. Logs may
include job name, counts, checkpoint number, duration, and exception type.
Avoid full records and connection strings.

## Exercises

1. Validate constructor inputs, especially non-blank job name and positive batch
   size.
2. Implement `run_once()` in the order above. Return read count, written count,
   and final checkpoint.
3. Build simple fakes for all four Protocols. Make the sink fail on a configured
   call.
4. With four records and batch size two, fail the second write. Assert that only
   checkpoint `2` was saved. Run again with a healthy sink and assert extraction
   resumes after `2`.
5. Reject duplicate IDs, non-positive or non-increasing sequences, and
   non-finite or non-positive money before the first sink call.
6. Emit success/failure and record-count metrics with only job and exception
   type tags. Do not use exception messages as tags.
7. Implement `validate_database_transport()`. Accept `postgresql`/`postgres`,
   allow local course hosts, and require `sslmode=require`, `verify-ca`, or
   `verify-full` for remote hosts.
8. Write a short runbook covering startup, health evidence, retry ownership,
   checkpoint inspection, safe replay, rollback, credential rotation, and
   escalation.

### Progressive hints

1. Validate the complete extracted sequence before starting writes.
2. Store the current checkpoint only after the corresponding sink call.
3. A fake checkpoint store needs `load()`, `save()`, and a history list.
4. `urllib.parse.urlsplit()` and `parse_qs()` can inspect transport fields; never
   include the original URL in an error.
5. Choose either the scheduler or the job as retry owner. Nested retry loops can
   multiply attempts unexpectedly.

## Optional live-DB capstone

Only after fake tests pass:

1. use a disposable course database;
2. create a temporary staging table `ON COMMIT DROP`;
3. implement a Psycopg sink with parameter binding or COPY;
4. store a test checkpoint in memory, not a persistent course table;
5. inject a failure before the second batch commit;
6. roll back and verify no persistent objects or rows remain.

```powershell
$env:DS60_DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
export DS60_DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
.venv/bin/python -m pytest bridge/tests -q
```

The repository's normal bridge test suite remains fake-backed and does not
contact this URL.

## Self-check

- Can the runner restart after every simulated failure point?
- Is a checkpoint never ahead of a confirmed sink write?
- Is a repeated batch safe at the sink?
- Can operators distinguish zero input, success, and failure from telemetry?
- Are credentials, payloads, and personal fields absent from logs and metrics?
- Does remote transport require TLS?
- Is the recovery procedure written for another person, not only remembered by
  the author?

## Common pitfalls

- **Checkpointing before write:** a crash can create silent data loss.
- **Assuming “exactly once”:** most distributed boundaries provide at-least-once
  behavior; idempotent sinks make replay safe.
- **Logging whole records on failure:** debugging creates a data leak.
- **High-cardinality metric labels:** monitoring cost and usability deteriorate.
- **Health checks that mutate data:** probes should be cheap and read-only.
- **Permanent broad database credentials:** use a dedicated role with only
  required schema and statement privileges.
- **No recovery rehearsal:** an untested runbook is a hypothesis.

## Next step

Revisit weak areas using the [bridge index](../README.md), then complete a small
project that replaces one fake adapter at a time while retaining the same
contracts and tests. Compare your design with
[the Day 8 solution notes](../solutions/day08_solutions.md); differences are
expected when your recovery contract is explicit and tested.
