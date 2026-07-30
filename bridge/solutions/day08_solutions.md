# Bridge Day 8 — Solution notes

Complete the [capstone starter](../lessons/day08_production_capstone.py) before
reviewing [day08_solution.py](day08_solution.py).

## Recovery invariant

The reference loads one checkpoint, validates the complete extracted sequence,
and handles bounded batches in this order:

1. write the batch;
2. save the batch's last sequence;
3. record the successful write count.

If the second batch fails, the first batch's checkpoint remains durable. A
restart asks the extractor only for later sequences. The sink still needs an
idempotency key because a network failure can make write outcome uncertain.

Input validation occurs before the first effect. Sequences must be positive and
strictly increasing after the checkpoint, IDs unique within a run, and amounts
finite.

## Observability and security

Metrics use stable job and exception-type tags. Logs contain job name, counts,
and exception type—never the exception message, records, or connection strings.
The runner re-raises failure so an external scheduler can mark the run failed.

`validate_database_transport()` checks scheme, host, and remote TLS mode without
returning or echoing the URL. Local course connections may omit TLS; remote
hosts require `require`, `verify-ca`, or `verify-full`.

## Tradeoffs

- Saving a checkpoint after every batch reduces replay but increases checkpoint
  writes. Larger checkpoint intervals trade recovery work for throughput.
- The runner validates all extracted records in memory. A streaming design
  needs incremental order checks and bounded extraction.
- Omitting exception messages and tracebacks at this boundary protects secrets
  but reduces diagnostics. A protected error store can retain richer traces
  under an explicit access and retention policy.
- URL query validation is a minimum transport guard, not full security.
  Certificate validation, secret storage, role privileges, rotation, network
  policy, statement timeouts, and audit requirements belong in deployment.
- Exactly-once processing is not claimed. Checkpoint ordering plus an
  idempotent sink provides recoverable at-least-once behavior.

The strongest capstone evidence is the failure test: the second batch fails,
checkpoint `2` remains, and the next run processes only sequences `3` and `4`.

## Exercise solutions

These walkthroughs align one-for-one with the learner and guide. The executable
reference is `bridge/solutions/day08_solution.py`; use it only after an honest attempt.

**Shared failure rule:** An advanced checkpoint or non-idempotent ambiguous sink write can permanently skip or duplicate records during recovery.

### Exercise 1 — Validation

**Prompt:** Validate constructor inputs, including non-blank job name and positive batch size,
before retaining dependencies.

**Approach:** Strip/check the job name, require `batch_size >= 1`, and store the injected
Protocol implementations. Keep defaults explicit and do not contact any dependency during
construction.

**Why this boundary matters:** Reject invalid orchestration configuration before the first
effect.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 2 — Orchestration

**Prompt:** Implement `run_once()` in load-extract-validate-batch-write-checkpoint order and
return read, written, and final checkpoint evidence.

**Approach:** Load the prior checkpoint, extract after it, validate all records, write
deterministic batches, save each batch's last sequence only after successful write, emit bounded
metrics, and return `JobResult`.

**Why this boundary matters:** Validate the full extracted sequence before the first sink call.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 3 — Test doubles

**Prompt:** Build extractor, sink, checkpoint, and metric fakes; configure the sink to fail on a
selected call.

**Approach:** Each fake records calls and owns no assertions. The failing sink raises on its
configured invocation after recording the attempted batch so the test can inspect recovery
evidence.

**Why this boundary matters:** Fakes should expose histories and deterministic failure switches.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 4 — Recovery test

**Prompt:** With four records and batch size two, fail write two, assert only checkpoint two
persists, then resume from two with a healthy sink.

**Approach:** The first run saves `[2]` and raises; the second extractor request is `2`, writes
records 3–4, and saves `4`. No checkpoint for the failed batch is recorded.

**Why this boundary matters:** Extraction on retry must receive the last durable checkpoint.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 5 — Record validation

**Prompt:** Reject duplicate IDs, non-positive/non-increasing sequences, and
non-finite/non-positive money before any sink effect.

**Approach:** Scan all extracted records once, tracking IDs and previous sequence, and raise on
the first invariant violation. The sink history must remain empty for every invalid fixture.

**Why this boundary matters:** Check global order/uniqueness after validating individual
records.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 6 — Observability

**Prompt:** Emit success/failure and record-count metrics with only job and exception-class
tags.

**Approach:** Use fixed metric names and a bounded job label plus exception type on failure.
Emit numeric counts as values, not tags, and never use the exception message.

**Why this boundary matters:** Keep messages, record IDs, checkpoints, and request IDs out of
metric dimensions.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 7 — Transport security

**Prompt:** Implement `validate_database_transport()` for PostgreSQL schemes, local course
hosts, and required TLS modes on remote hosts.

**Approach:** Accept `postgresql`/`postgres`; permit loopback/local course hosts without forced
TLS; require `sslmode` in `require`, `verify-ca`, or `verify-full` remotely; raise constant safe
messages.

**Why this boundary matters:** Parse without echoing; local and remote host policies differ.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 8 — Runbook

**Prompt:** Write operational steps for startup, health evidence, retry ownership, checkpoint
inspection, replay, rollback, credential rotation, and escalation.

**Approach:** The runbook names the disposable/production boundary, commands or queries that
reveal no credentials, one retry owner, how to compare sink/checkpoint state, when to pause, and
how to rotate without logging the URL.

**Why this boundary matters:** Every action needs prerequisites, expected evidence, and a stop
condition.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 9 — No-op behavior

**Prompt:** Define the result and metrics when extraction returns no records.

**Approach:** Return zero read/written with the loaded checkpoint unchanged, emit a bounded
success/no-op count, and leave sink/checkpoint save histories empty.

**Why this boundary matters:** A no-op should not write or advance a checkpoint.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 10 — Checkpoint validation

**Prompt:** Detect records at or below the loaded checkpoint and out-of-order extractor results
before writing.

**Approach:** Require every sequence to be greater than the loaded checkpoint and strictly
increasing. Reject a stale or regressing response with no sink calls.

**Why this boundary matters:** Do not assume an injected extractor obeys its Protocol's semantic
promise.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 11 — Ambiguous writes

**Prompt:** Explain recovery when the sink commits a batch but the client raises before seeing
success.

**Approach:** The sink must be idempotent on record ID or expose commit evidence. On retry,
replaying the batch is safe only under that contract; otherwise pause and reconcile before
advancing the checkpoint.

**Why this boundary matters:** Post-write checkpoint ordering alone cannot prevent a duplicate
replay.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 12 — Metric design

**Prompt:** Classify which fields belong in metrics, structured logs, or neither, and test
cardinality.

**Approach:** Metrics receive bounded job/outcome/class tags; redacted structured logs may hold
a correlation ID and checkpoint; record payloads, amounts, URLs, and exception messages belong
in neither default channel.

**Why this boundary matters:** Observability channels have different retention and indexing
costs.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 13 — Health model

**Prompt:** Separate process liveness, dependency readiness, and last-run success for the job.

**Approach:** Liveness checks the process loop only; readiness verifies required
dependencies/configuration without mutation; run status reports the latest job evidence. Do not
collapse them into one green flag.

**Why this boundary matters:** A process can be alive while unable to make safe progress.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 14 — URL edge cases

**Prompt:** Test loopback names, IPv4/IPv6, missing host, case-insensitive TLS values,
unsupported schemes, and remote insecure modes.

**Approach:** Treat `localhost`, `127.0.0.1`, and `::1` as local; validate a database/host
exists as policy requires; case-normalize `sslmode`; reject unsupported/missing remote modes
without returning the original URL.

**Why this boundary matters:** Normalize parsed components and keep every failure message
secret-free.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 15 — Operations drill

**Prompt:** Simulate credential rotation and prove the runner can restart without resetting a
valid checkpoint.

**Approach:** Stop acquisition, rotate the external secret, validate a new connection through
the safe boundary, resume with the same checkpoint store, and verify extraction begins after the
durable sequence.

**Why this boundary matters:** Credentials identify access, not processing position.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 16 — Invariant testing

**Prompt:** Generate failure positions across multiple batch sizes and prove persisted
checkpoints always correspond to fully successful batches.

**Approach:** For each batch size/failure call, compute the last completed batch end and assert
saved history never exceeds it. Resume and reconcile that every logical record is eventually
written under an idempotent sink.

**Why this boundary matters:** Vary boundaries while holding deterministic records and fakes.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.
