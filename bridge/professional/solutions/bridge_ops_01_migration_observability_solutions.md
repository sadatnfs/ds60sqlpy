# BRIDGE-OPS-01 — Solution reasoning

Start with the
[learner file](../lessons/bridge_ops_01_migration_observability.py). The
executable reference is
[bridge_ops_01_migration_observability_solution.py](bridge_ops_01_migration_observability_solution.py).

## Immutable history and planning

`Migration` validates an ordered ID, non-empty description, at least one
command, and a separate verification query. Its checksum is deterministic JSON
over identity, description, command text, bound scalar values, and
verification. `plan_pending()` rejects duplicate or reordered source,
database-only IDs, and changed checksums before returning pending versions.

The checksum is drift detection, not a signature or authorization mechanism.
Repository review and release controls decide which migration source is
trusted.

## Parameter and identifier boundaries

`SqlCommand` stores SQL text and a parameter tuple separately. The reference
checks that every `%s` has one value, then the database adapter calls
`execute(text, params)`. The metadata lookup, metadata insert, backfill value,
and verification filters all use this boundary.

Schema, table, and column names are immutable trusted migration source. Psycopg
cannot bind identifiers as values. A product that permits dynamic identifiers
needs an allowlist plus `psycopg.sql.Identifier`; Jinja, f-strings, and manual
quoting are not parameter binding.

## Transaction, retry, and concurrency boundaries

Each attempt opens a new session, obtains a transaction-scoped advisory lock,
re-reads the metadata row, applies commands, verifies, records metadata, and
commits. Failures roll back and close before the injected sleeper runs. Only
the fake transient exception, selected transaction/lock SQLSTATEs, and
connection-class SQLSTATEs retry.

The advisory lock prevents two well-behaved course runners from applying the
same version concurrently. The metadata primary key remains a final invariant.
Production migration tools normally supply their own lock and history table;
do not stack independent lock schemes without understanding their order.

An uncertain commit is safe because schema change and metadata row commit in
the same transaction. A new attempt sees the matching checksum after acquiring
the lock and skips. This is stronger than making every DDL statement use
`IF NOT EXISTS`, which can hide an unexpected object shape.

## Observability and probes

`JsonEventLogger` emits deterministic JSON. Callers provide request ID,
migration ID, attempt, duration, outcome, retry flag, and exception type.
`redact_fields()` replaces sensitive key names and credential-bearing URL
shapes. Orchestration never passes statement parameters or exception messages
in the first place; redaction is a second boundary, not permission to log
everything.

Metrics use migration ID and a bounded outcome label. Request IDs remain in
logs because they would create high-cardinality metrics.

`liveness()` is process-local. `check_readiness()` uses only reads, checks the
metadata table, and reuses `plan_pending()` for missing or drifted versions.
It reports the exception type on probe failure without leaking its message.

## Recovery reasoning

`decide_recovery()` refuses to choose before diagnosis is confirmed. If
committed schema has received writes, it selects a forward fix only when that
path was rehearsed. It selects release rollback only when the previous
application is compatible and reversal was rehearsed. All unsupported
combinations pause.

The result is evidence organization, never an automatic migration command.
Operators still assess data loss, locks, traffic, backups, ownership, and the
incident's actual failure mode.

## Optional live adapter

The default module imports no Psycopg code. `run_live()` imports Psycopg 3 at
the optional boundary and creates one connection per attempted transaction.
`require_course_database_url()` reads only `DS60_DATABASE_URL`, validates the
PostgreSQL scheme and exact disposable database name, and never returns the URL
to logs or output.

The two example migrations create a lab table and then make an additive
change. Their source SQL is intentionally not made superficially idempotent;
the metadata transaction supplies idempotency and exposes partial or drifted
state instead of concealing it.

## Tradeoffs

- A SHA-256 content checksum is portable and easy to audit, but it treats
  semantically harmless formatting edits as drift. That is intentional for
  immutable migration history.
- A single advisory-lock key serializes this course's migration runner.
  Organizations need a collision-safe lock convention and one recognized
  migration owner.
- Connection-class errors retry because metadata makes an uncertain commit
  idempotent. A general application transaction may not have that property.
- Exception types are safe and low-cardinality but less diagnostic than a
  protected trace store. Rich diagnostics need explicit access, retention, and
  redaction policy.
- `check_readiness()` opens a database connection per call. Real services often
  cache bounded state or separate startup readiness from high-frequency probes.
- Requiring an exact database name is a course safety rail, not a general
  production authorization control.
- The recovery decision model is intentionally conservative. It cannot replace
  tested backups, change review, ownership, or incident command.

Add tests for checksum drift, concurrent re-check behavior, final-attempt
failure, commit uncertainty, rollback/close failures, sensitive telemetry,
readiness drift, and every recovery branch before adapting this pattern.

## Exercise solutions

These walkthroughs map one-for-one to the answer-free learner artifact and
companion guide. The executable reference is `bridge/professional/solutions/bridge_ops_01_migration_observability_solution.py`.

**Shared failure rule:** Mutable history, retry after uncertain commit without re-checking metadata, or recovery without complete evidence can corrupt schema state.

### Exercise 1 — Validation

**Prompt:** Implement `Migration` validation and a stable checksum over identity, description,
command text/parameters, and verification.

**Approach:** Validate non-blank ordered ID, description, at least one command, and
verification; serialize fields into a deterministic JSON-compatible form and hash with SHA-256.

**Why:** Canonical serialization must distinguish structure and parameter types without
depending on object repr.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 2 — Redaction

**Prompt:** Implement `redact_fields()` for sensitive key names, URL-shaped values,
non-serializable objects, and ordinary scalars.

**Approach:** Replace credential-bearing keys/URL values with a marker, retain bounded JSON
scalars, convert unsupported objects to safe type labels, and recursively avoid payload dumps.

**Why:** Use key classification and safe type conversion; never echo rejected values.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 3 — Planning

**Prompt:** Implement `plan_pending()` with duplicate/order validation, unknown applied-version
rejection, and checksum-drift detection.

**Approach:** Validate unique increasing IDs, ensure every applied ID exists and matches
checksum, reject gaps/unknown versions, then return unapplied migrations in canonical order.

**Why:** Applied history is immutable and must be a prefix of known ordered migrations.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 4 — Test double

**Prompt:** Build a recording session fake that stores SQL separately from parameter tuples and
never parses PostgreSQL through SQLite.

**Approach:** Record execute calls, queue deterministic result objects, and track
commit/rollback/close events. Test SQL dialect behavior only in optional PostgreSQL integration.

**Why:** Model transactional state and prepared query results explicitly.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 5 — Delivery

**Prompt:** Implement the documented nine-step delivery order and prove rollback/close happen
before injected retry delay.

**Approach:** Encode the order directly, classify only retryable failures, roll back and close
in the attempt's exception path, and let the outer retry call its fake sleeper afterward.

**Why:** One attempt must acquire, lock, re-check, apply, verify, record, commit, close, then
report.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 6 — Commit uncertainty

**Prompt:** Simulate an uncertain commit whose retry sees a matching metadata row and prove
commands are not applied twice.

**Approach:** On retry, read the recorded checksum; a match means the first attempt committed,
so mark it skipped/applied evidence without re-running commands. Drift must fail closed.

**Why:** Re-check immutable metadata under lock before every attempt.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 7 — Observability

**Prompt:** Add event and metric fakes; require request/migration IDs in logs, exclude request
IDs from metric tags, and prove secrets are absent.

**Approach:** Emit redacted structured events with correlation IDs, count/observe with fixed
tags such as outcome/migration class, and test sentinel secrets across every field/message.

**Why:** Logs support correlation; metrics require bounded dimensions.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 8 — Readiness

**Prompt:** Implement read-only readiness for current, pending, drifted, and unreachable states
while keeping liveness database-independent.

**Approach:** Probe metadata without writes, compare current/target/checksums, return bounded
reasons, and map connection failure to not-ready. Liveness remains a local process response.

**Why:** Readiness describes safe traffic acceptance, not process existence.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 9 — Recovery

**Prompt:** Build a scenario table for recovery decisions, including incomplete evidence that
must pause.

**Approach:** Return pause when diagnosis/state is incomplete; choose forward fix only with
confirmed/rehearsed safe progress; choose rollback release only when prior compatibility and
rollback evidence are established.

**Why:** Destructive or forward actions require rehearsed, compatible evidence.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 10 — Optional integration

**Prompt:** After fake tests, run the disposable live lab twice and inspect migration metadata
with a read-only query.

**Approach:** Gate on environment/opt-in, parameterize values, run against the course schema,
assert first applied/second skipped plus matching checksum, then remove lab objects through the
documented rollback-safe cleanup.

**Why:** The second run demonstrates idempotency; cleanup evidence is part of completion.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 11 — Immutability

**Prompt:** Change only SQL whitespace after a migration is applied and decide whether checksum
drift should be accepted.

**Approach:** The reference treats any serialized content change as drift. Create a new
migration for intentional changes; do not normalize arbitrary SQL in a way that can hide
meaningful edits.

**Why:** A stored checksum is an immutable history contract, not a semantic SQL parser.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 12 — Concurrency

**Prompt:** Model two deployers contending for the same advisory lock and specify
timeout/ownership behavior.

**Approach:** Acquire a stable namespaced advisory transaction lock, let the second wait or fail
under a configured lock timeout, and re-plan after acquisition rather than using stale pre-lock
state.

**Why:** Only one delivery transaction may make planning decisions at a time.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 13 — PostgreSQL semantics

**Prompt:** Identify which DDL is transactional in PostgreSQL and how non-transactional commands
alter the migration policy.

**Approach:** Most PostgreSQL DDL is transactional, but commands such as `CREATE INDEX
CONCURRENTLY` have restrictions. Classify or forbid such commands in the standard runner and use
a separately designed/rehearsed workflow.

**Why:** Do not assume every administrative statement can share ordinary transaction rollback.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 14 — Timeouts

**Prompt:** Set statement and lock timeouts per attempt without leaking settings to later pooled
work.

**Approach:** Issue parameter-safe `SET LOCAL` or trusted constant settings after beginning the
transaction, test their order before commands, and rely on transaction end to restore defaults.

**Why:** Transaction-local settings should expire with commit/rollback.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 15 — Telemetry design

**Prompt:** Define a bounded migration metric schema and a redaction test for exception objects
and URL-like fields.

**Approach:** Prefer outcome/stage/error-class tags and numeric duration/attempts; keep
request/migration IDs in logs unless the migration set is explicitly bounded; sanitize exception
details before emission.

**Why:** Migration IDs may still become unbounded over years; choose dimensions deliberately.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 16 — Probe semantics

**Prompt:** Distinguish current-but-stale application readiness from database reachability and
migration currency.

**Approach:** Reachability proves a read connection; schema readiness proves expected
migration/checksum state; application freshness/version compatibility is separate evidence.
Report reasons independently.

**Why:** Each probe should answer one operational question.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 17 — Decision analysis

**Prompt:** Compare forward fix and release rollback when the new schema has already received
writes.

**Approach:** Default to pause unless compatibility and data transformation evidence exists.
Forward fix is often safer after new writes; rollback release requires proof the old app can
read/write the evolved data.

**Why:** Data written under the new contract can make old code incompatible even if DDL reversal
is possible.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 18 — Expand-contract

**Prompt:** Design a three-release expand/migrate/contract sequence for renaming a populated
column.

**Approach:** Add the new nullable column, dual-write/backfill/verify, switch readers and
enforce constraints, then remove the old column only after compatibility and rollback windows
close.

**Why:** Maintain compatibility while old and new application versions overlap.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 19 — Cleanup

**Prompt:** Prove the optional live lab leaves no table, metadata row, lock, connection, or
credential-bearing output behind.

**Approach:** Run read-only catalog checks after cleanup, close every session, verify lock
absence, clear captured output, and scan logs/notebook/test artifacts for URL or secret
sentinels.

**Why:** A passing mutation test is incomplete without postconditions.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 20 — Failure simulation

**Prompt:** Inject a network-like error immediately after fake commit and require the retry to
gather evidence rather than blindly replay.

**Approach:** Mark the fake metadata committed, raise to the client, then on retry
re-lock/re-read and accept only the matching checksum. A missing or mismatched row must not be
guessed into success.

**Why:** Client exceptions after commit do not prove server rollback.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.
