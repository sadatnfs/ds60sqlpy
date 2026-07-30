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
