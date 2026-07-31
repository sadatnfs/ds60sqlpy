# Bridge Day 8 — Production capstone: observability, security, and recovery

**Level:** Advanced  
**Prerequisite:** [Bridge Day 7](day07_async_bounded_concurrency.md)

## Why this matters

Production readiness is not a framework choice. It is evidence that a program
behaves predictably on success, invalid input, partial failure, retry, restart,
and shutdown—without exposing secrets. This capstone keeps effectful adapters
small and makes orchestration order observable with fakes before any live
database run.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\lessons\day08_production_capstone.py
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/lessons/day08_production_capstone.py
.venv/bin/python -m pytest bridge/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/lessons/day08_production_capstone.py`, and use small fakes or recording doubles for the
default evidence path. Any PostgreSQL step is optional, explicitly gated, and restricted to `DS60_DATABASE_URL` plus the disposable `advanced_sql_training` database. Never place a credential in source, notebook output, test fixtures, or logs.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

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


<!-- BEGIN BRIDGE ENRICHMENT: DEEP DIVE -->
## Mental model: the recovery invariant is the product

The capstone is not a collection of helper functions; it is one recovery
contract. After every successful batch, durable state must say exactly how far
the sink can safely resume. That means the sink writes the batch before the
checkpoint advances. Advancing first can skip data permanently. Writing first
can replay after an uncertain result, so the sink also needs a stable
idempotency policy.

Write the state transition before implementing orchestration:

```python
events: list[str] = []


def finish_batch(last_sequence: int) -> None:
    events.append("write")
    events.append(f"checkpoint:{last_sequence}")
    events.append("metric:written")


finish_batch(20)
assert events == ["write", "checkpoint:20", "metric:written"]
```

Validate the entire extracted sequence before the first effect in this compact
version. Record IDs must be non-blank and unique within the run, sequences must
be positive and strictly increase after the saved checkpoint, and amounts must
be finite and positive. A streaming implementation can validate
incrementally, but it must preserve the same invariant across batch
boundaries.

Observability is evidence, not a data dump. Metrics need bounded labels such as
job and outcome. Logs may carry a request or run identifier, but should not
contain records, credentials, complete URLs, or raw exception messages. Emit a
failure event and re-raise so the external scheduler still sees failure.
Separate process liveness, dependency readiness, and last-run health because
they answer different operational questions.

Transport URL validation is only an early guard. A remote PostgreSQL endpoint
must require TLS, while a loopback course database may use local policy. The
URL must never appear in the error. Real deployment also needs least-privilege
roles, rotation, certificate validation, statement timeouts, protected traces,
and rehearsed recovery.

The most valuable test injects failure into the second batch. It proves the
first checkpoint remains, the failed batch does not advance it, cleanup runs,
and a restart requests only work after the durable checkpoint. Run variations
across batch sizes and failure positions to show the invariant is structural,
not an accident of one example.
<!-- END BRIDGE ENRICHMENT: DEEP DIVE -->

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
   - **Verify:** Construct runners with blank names and non-positive batch sizes; assert `ValueError` before any dependency is retained or called, while a valid constructor has zero effects.
2. **Orchestration:** Implement `run_once()` in load-extract-validate-batch-write-checkpoint
   order and return read, written, and final checkpoint evidence.
   - **Progressive hint:** Validate the full extracted sequence before the first sink call.
   - **Verify:** For a two-batch run, assert event order `load, extract, validate, write, checkpoint` per batch and compare `JobResult` read/written counts plus final checkpoint.
3. **Test doubles:** Build extractor, sink, checkpoint, and metric fakes; configure the sink to
   fail on a selected call.
   - **Progressive hint:** Fakes should expose histories and deterministic failure switches.
   - **Verify:** Configure fakes with public call lists and sink failure index; assert inputs, batches, checkpoint saves, metric events, and failure call are all independently inspectable.
4. **Recovery test:** With four records and batch size two, fail write two, assert only
   checkpoint two persists, then resume from two with a healthy sink.
   - **Progressive hint:** Extraction on retry must receive the last durable checkpoint.
   - **Verify:** With sequences 1–4 and batch size two, fail write two; assert checkpoint `2`, then restart and assert only sequences 3–4 are written and checkpoint becomes `4`.
5. **Record validation:** Reject duplicate IDs, non-positive/non-increasing sequences, and
   non-finite/non-positive money before any sink effect.
   - **Progressive hint:** Check global order/uniqueness after validating individual records.
   - **Verify:** Parameterize duplicate IDs, sequence zero, repeated/decreasing sequence, `NaN`/infinity, and non-positive amount; assert each fails before the sink or checkpoint is touched.
6. **Observability:** Emit success/failure and record-count metrics with only job and
   exception-class tags.
   - **Progressive hint:** Keep messages, record IDs, checkpoints, and request IDs out of metric
     dimensions.
   - **Verify:** Inspect metrics/logs for success and failure: tags contain only job/outcome/exception class, counts are correct, and records, URLs, and exception messages are absent.
7. **Transport security:** Implement `validate_database_transport()` for PostgreSQL schemes,
   local course hosts, and required TLS modes on remote hosts.
   - **Progressive hint:** Parse without echoing; local and remote host policies differ.
   - **Verify:** Accept local PostgreSQL URLs and remote URLs with `require`, `verify-ca`, or `verify-full`; reject missing host, wrong scheme, and insecure remote mode without echoing URL.
8. **Runbook:** Write operational steps for startup, health evidence, retry ownership,
   checkpoint inspection, replay, rollback, credential rotation, and escalation.
   - **Progressive hint:** Every action needs prerequisites, expected evidence, and a stop
     condition.
   - **Verify:** Produce a runbook checklist covering startup, liveness/readiness/last-run evidence, retry owner, checkpoint query, replay, rollback, rotation, escalation owner, and stop condition.
9. **No-op behavior:** Define the result and metrics when extraction returns no records.
   - **Progressive hint:** A no-op should not write or advance a checkpoint.
   - **Verify:** For empty extraction, assert zero read/written counts, unchanged checkpoint, no sink or checkpoint-save call, and one bounded successful no-op metric/event.
10. **Checkpoint validation:** Detect records at or below the loaded checkpoint and out-of-order
   extractor results before writing.
   - **Progressive hint:** Do not assume an injected extractor obeys its Protocol's semantic
     promise.
   - **Verify:** Feed a record equal to the checkpoint and a decreasing pair; assert each raises before the first write and leaves the stored checkpoint unchanged.
11. **Ambiguous writes:** Explain recovery when the sink commits a batch but the client raises
   before seeing success.
   - **Progressive hint:** Post-write checkpoint ordering alone cannot prevent a duplicate
     replay.
   - **Verify:** Model server commit followed by client error; assert restart consults sink idempotency evidence and checkpoint state before replaying rather than advancing blindly.
12. **Metric design:** Classify which fields belong in metrics, structured logs, or neither, and
   test cardinality.
   - **Progressive hint:** Observability channels have different retention and indexing costs.
   - **Verify:** Classify job/outcome/error class/counts as bounded metrics, run/request ID as structured log fields, and record IDs/payloads/URLs as neither; test the resulting cardinality.
13. **Health model:** Separate process liveness, dependency readiness, and last-run success for
   the job.
   - **Progressive hint:** A process can be alive while unable to make safe progress.
   - **Verify:** Return independent evidence for process liveness, dependency readiness, and last-run success; force each one false while the other two remain true.
14. **URL edge cases:** Test loopback names, IPv4/IPv6, missing host, case-insensitive TLS
   values, unsupported schemes, and remote insecure modes.
   - **Progressive hint:** Normalize parsed components and keep every failure message
     secret-free.
   - **Verify:** Parameterize localhost, loopback IPv4/IPv6, missing host, mixed-case TLS values, wrong schemes, and insecure remote URLs; compare exact accept/reject outcomes and safe messages.
15. **Operations drill:** Simulate credential rotation and prove the runner can restart without
   resetting a valid checkpoint.
   - **Progressive hint:** Credentials identify access, not processing position.
   - **Verify:** Swap a secret-bearing URL between runs without changing checkpoint storage; assert the new adapter is used, no URL is logged, and processing resumes after the valid checkpoint.
16. **Invariant testing:** Generate failure positions across multiple batch sizes and prove
   persisted checkpoints always correspond to fully successful batches.
   - **Progressive hint:** Vary boundaries while holding deterministic records and fakes.
   - **Verify:** Generate batch sizes and failure positions; after every failed run, assert persisted checkpoint equals the last sequence of a fully completed batch and never a failed batch.

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


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-07`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-08: Production Capstone.
Direct catalog prerequisites: bridge-07. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/companion-guides/day08_production_capstone.md
Learner artifact: bridge/lessons/day08_production_capstone.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

Revisit weak areas using the [bridge index](../README.md), then complete a small
project that replaces one fake adapter at a time while retaining the same
contracts and tests. Compare your design with
[the Day 8 solution notes](../solutions/day08_solutions.md); differences are
expected when your recovery contract is explicit and tested.
