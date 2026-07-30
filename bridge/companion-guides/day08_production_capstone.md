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

### Practice contract

- **Focus:** Orchestrate a restart-safe batch job through injected effects, validation-before-write, post-write checkpoints, bounded observability, and safe database transport.
- **Assumptions:** Records have strictly increasing positive sequences and finite positive Decimal amounts; a checkpoint advances only after its batch write succeeds.
- **Primary failure mode:** An advanced checkpoint or non-idempotent ambiguous sink write can permanently skip or duplicate records during recovery.
- **Evidence loop:** predict the boundary, implement the smallest change,
  verify success and failure with a deterministic fake, then explain which
  behavior still requires an explicitly enabled PostgreSQL integration test.

1. **Validation:** Validate constructor inputs, including non-blank job name and positive batch
   size, before retaining dependencies.
   - **Progressive hint:** Reject invalid orchestration configuration before the first effect.
2. **Orchestration:** Implement `run_once()` in load-extract-validate-batch-write-checkpoint
   order and return read, written, and final checkpoint evidence.
   - **Progressive hint:** Validate the full extracted sequence before the first sink call.
3. **Test doubles:** Build extractor, sink, checkpoint, and metric fakes; configure the sink to
   fail on a selected call.
   - **Progressive hint:** Fakes should expose histories and deterministic failure switches.
4. **Recovery test:** With four records and batch size two, fail write two, assert only
   checkpoint two persists, then resume from two with a healthy sink.
   - **Progressive hint:** Extraction on retry must receive the last durable checkpoint.
5. **Record validation:** Reject duplicate IDs, non-positive/non-increasing sequences, and
   non-finite/non-positive money before any sink effect.
   - **Progressive hint:** Check global order/uniqueness after validating individual records.
6. **Observability:** Emit success/failure and record-count metrics with only job and
   exception-class tags.
   - **Progressive hint:** Keep messages, record IDs, checkpoints, and request IDs out of metric
     dimensions.
7. **Transport security:** Implement `validate_database_transport()` for PostgreSQL schemes,
   local course hosts, and required TLS modes on remote hosts.
   - **Progressive hint:** Parse without echoing; local and remote host policies differ.
8. **Runbook:** Write operational steps for startup, health evidence, retry ownership,
   checkpoint inspection, replay, rollback, credential rotation, and escalation.
   - **Progressive hint:** Every action needs prerequisites, expected evidence, and a stop
     condition.
9. **No-op behavior:** Define the result and metrics when extraction returns no records.
   - **Progressive hint:** A no-op should not write or advance a checkpoint.
10. **Checkpoint validation:** Detect records at or below the loaded checkpoint and out-of-order
   extractor results before writing.
   - **Progressive hint:** Do not assume an injected extractor obeys its Protocol's semantic
     promise.
11. **Ambiguous writes:** Explain recovery when the sink commits a batch but the client raises
   before seeing success.
   - **Progressive hint:** Post-write checkpoint ordering alone cannot prevent a duplicate
     replay.
12. **Metric design:** Classify which fields belong in metrics, structured logs, or neither, and
   test cardinality.
   - **Progressive hint:** Observability channels have different retention and indexing costs.
13. **Health model:** Separate process liveness, dependency readiness, and last-run success for
   the job.
   - **Progressive hint:** A process can be alive while unable to make safe progress.
14. **URL edge cases:** Test loopback names, IPv4/IPv6, missing host, case-insensitive TLS
   values, unsupported schemes, and remote insecure modes.
   - **Progressive hint:** Normalize parsed components and keep every failure message
     secret-free.
15. **Operations drill:** Simulate credential rotation and prove the runner can restart without
   resetting a valid checkpoint.
   - **Progressive hint:** Credentials identify access, not processing position.
16. **Invariant testing:** Generate failure positions across multiple batch sizes and prove
   persisted checkpoints always correspond to fully successful batches.
   - **Progressive hint:** Vary boundaries while holding deterministic records and fakes.

### Before opening the solution

- State the input/output and ownership boundary in one sentence.
- Show one normal case, one edge case, and one failure case.
- Inspect recorded calls rather than relying on plausible output.
- Confirm no credential, payload, or high-cardinality identifier was emitted.


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
