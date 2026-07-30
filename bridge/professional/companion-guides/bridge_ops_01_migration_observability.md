# BRIDGE-OPS-01 — Migration delivery and application observability

## Level and prerequisites

**Level:** Advanced  
**Stable lesson ID:** `bridge-ops-01`  
**Catalog prerequisites:** `sql-found-02` and `bridge-08`  
**Prerequisites:** SQL-FOUND-02, [Bridge Day 4](../../companion-guides/day04_transactions_idempotency_retries.md),
[Bridge Day 5](../../companion-guides/day05_db_testing_fixtures_doubles.md), and
[Bridge Day 8](../../companion-guides/day08_production_capstone.md). Days 4
and 5 are earlier steps within the sequential bridge path.

This cumulative lab connects database change delivery to application behavior.
A migration is not finished merely because one `ALTER TABLE` succeeded. It
also needs immutable history, a transaction boundary, verification, retry and
idempotency rules, useful telemetry, readiness evidence, and a rehearsed
recovery choice.

The default path uses Protocol-based fakes and does not need PostgreSQL. The
optional live path is restricted to `DS60_DATABASE_URL` and the disposable
`advanced_sql_training` database. It creates two course-owned lab objects in
the resettable `training` schema:

- `training.ds60_schema_migrations`
- `training.bridge_release_lab`

Never run the live lab against a production, shared, or valuable database.

Run the answer-free starter from the repository root:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\professional\lessons\bridge_ops_01_migration_observability.py
```

```bash
# macOS/Linux
.venv/bin/python bridge/professional/lessons/bridge_ops_01_migration_observability.py
```

## Learning objectives

By the end, you can:

- model immutable, ordered migrations and detect checksum drift;
- keep trusted SQL structure separate from bound data values;
- apply one migration in one explicit transaction and verify it before commit;
- retry only classified transient failures using a fresh session;
- make an uncertain commit safe to retry with migration metadata;
- emit redacted structured logs and low-cardinality metrics carrying request
  and migration IDs;
- distinguish liveness from database-backed readiness;
- choose forward-fix, rollback, or pause based on recorded evidence.

## Vocabulary and concepts

| Term | Meaning |
|---|---|
| migration ID | Stable ordered identity such as `20260730_002_release_source` |
| checksum | Hash of immutable migration content used to detect edited history |
| migration metadata | Table recording which version and checksum committed |
| advisory lock | PostgreSQL transaction-scoped coordination lock used here to serialize runners |
| expand–migrate–contract | Add compatible shape, move data/traffic, then remove old shape later |
| idempotent delivery | Repeating a migration attempt produces no second logical change |
| SQLSTATE | PostgreSQL's machine-readable error classification |
| structured log | Event plus named fields rather than an interpolated prose message |
| metric cardinality | Number of distinct label combinations a metric can produce |
| liveness | Evidence that the process itself can respond |
| readiness | Evidence that the process can safely serve its intended traffic |
| forward-fix | Apply a new corrective change without reversing committed data shape |
| rollback | Return application or schema state to a previously rehearsed compatible version |

## Worked example / walkthrough

### 1. Plan immutable migrations

The reference model stores an ID, description, trusted SQL commands, and a
read-only verification query. IDs must be unique and lexically ordered. Once a
checksum is recorded, editing that migration is drift and must stop delivery.
Create a new migration instead.

```python
Migration(
    migration_id="20260730_002_release_source",
    description="Expand the lab with an additive source label",
    commands=(
        SqlCommand("ALTER TABLE training.bridge_release_lab ADD COLUMN source_label text"),
        SqlCommand(
            "UPDATE training.bridge_release_lab SET source_label = %s "
            "WHERE source_label IS NULL",
            ("legacy",),
        ),
    ),
    verification=SqlCommand(
        "SELECT count(*) = 1 FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s AND column_name = %s",
        ("training", "bridge_release_lab", "source_label"),
    ),
)
```

Object names are trusted migration source code. `%s` placeholders bind values
such as `"legacy"` and the three catalog filters. Psycopg parameters cannot
stand for a table or column name. If application input genuinely selects an
identifier, first enforce an allowlist and then use
`psycopg.sql.Identifier`; do not use an f-string.

### 2. Deliver one complete transaction per attempt

The reference performs this sequence for each version:

1. open a fresh session;
2. acquire a transaction-scoped advisory lock;
3. re-read that migration's metadata row;
4. skip only when the recorded checksum matches;
5. execute trusted commands with separate parameter tuples;
6. execute a read-only verification query;
7. insert the migration ID, checksum, and request ID with parameters;
8. commit;
9. close the session.

Any failure rolls back before classification. A retry opens a new session and
repeats the *complete* transaction. It never retries a statement inside an
already-aborted transaction.

The metadata insert and schema change commit atomically. If the server commits
but the client loses the response, the next attempt finds the matching metadata
row and skips safely. This is the idempotency boundary.

### 3. Classify retries narrowly

The fake-friendly `RetryableDatabaseError` keeps default tests deterministic.
The reference also recognizes PostgreSQL serialization failure (`40001`),
deadlock detected (`40P01`), lock not available (`55P03`), and connection-class
SQLSTATE values. Validation errors, checksum drift, syntax errors, and
constraint violations are not automatically retryable.

Bound attempts and exponential delay limit outage amplification. A production
policy commonly adds jitter, a total deadline, and a deployment-level circuit
breaker. Those policies should remain injected so tests never sleep.

### 4. Emit safe operational evidence

Each event includes stable fields:

```text
event=migration.attempt_started
request_id=change-482
migration_id=20260730_002_release_source
attempt=1
```

Failure events include `error_type` and `retrying`, not the exception message.
The redactor removes credential-like field names and URL-shaped values. Never
send a connection URL, statement parameters, record payload, or raw exception
to logs or metric tags.

Useful low-cardinality metrics include:

```text
migration_attempts_total{migration_id="20260730_002_release_source"}
migration_outcomes_total{migration_id="...",outcome="applied"}
migration_duration_seconds{migration_id="..."}
```

Do not label metrics with request IDs. They are useful in logs, but every
request ID is distinct and would create unbounded metric cardinality.

### 5. Separate health from readiness

`liveness()` has no database dependency. It proves only that the process can
answer. `check_readiness()` performs read-only checks:

- `SELECT 1` succeeds;
- the migration metadata table exists;
- all expected IDs exist;
- stored checksums match current source.

A live process with a missing migration is *not ready*. A probe must not create
tables, apply migrations, or repair state.

### 6. Make recovery evidence explicit

`decide_recovery()` is a decision aid, not automation. It pauses when diagnosis
is unconfirmed. Once new schema shape has received writes, an unrehearsed
reverse migration may lose data, so only a rehearsed forward fix is selected.
A release rollback is selected only when the previous application is compatible
and the reverse path was rehearsed. Otherwise the correct result is to gather
more evidence.

Capture the evidence before release:

- compatibility test results for old and new application versions;
- migration and verification output;
- request/change ID and exact checksum;
- whether writes reached the new shape;
- forward-fix and reverse rehearsal results;
- owner and stop/go decision.

### 7. Optional live lab

First reset and verify only the disposable course database using the canonical
PostgreSQL setup instructions. Then provide the connection string only to the
current process environment.

```powershell
# Windows PowerShell
$env:DS60_DATABASE_URL = Read-Host "Paste the disposable course PostgreSQL URL"
.\.venv\Scripts\python.exe `
  bridge\professional\solutions\bridge_ops_01_migration_observability_solution.py `
  --live --request-id learning-bridge-ops-01
```

```bash
# macOS/Linux
read -r -s -p "Disposable course PostgreSQL URL: " DS60_DATABASE_URL
export DS60_DATABASE_URL
printf '\n'
.venv/bin/python \
  bridge/professional/solutions/bridge_ops_01_migration_observability_solution.py \
  --live --request-id learning-bridge-ops-01
```

The command rejects any database name other than
`advanced_sql_training`. It prints counts and readiness only, never the URL.
Running it again should report both migrations as skipped with matching
checksums. Resetting `training` through the course setup removes the lab state.

## Exercises

1. Implement validation and stable checksum generation for `Migration`.
2. Implement `redact_fields()`. Test sensitive key names, URL-shaped values,
   non-serializable objects, and ordinary scalar fields.
3. Implement `plan_pending()`. Reject duplicate or out-of-order IDs, unknown
   applied versions, and checksum drift.
4. Build a recording session fake. Record SQL text separately from parameter
   tuples and never parse PostgreSQL with SQLite.
5. Implement delivery in the nine-step order above. Make the fake fail once
   with `RetryableDatabaseError` and prove that rollback and close precede the
   injected delay.
6. Simulate an uncertain commit by making the retry observe a matching metadata
   row. Prove that commands are not applied twice.
7. Add structured event and metric fakes. Assert request/migration IDs are
   present in logs, request IDs are absent from metric tags, and secrets never
   appear.
8. Implement read-only readiness for current, pending, drifted, and unreachable
   states. Keep liveness independent of the database.
9. Build a table of recovery scenarios and expected decisions. Include one
   incomplete-evidence case that must pause.
10. Only after fake tests pass, run the optional live lab twice and inspect the
    metadata with a read-only query.

## Self-check

- Can an applied migration's source change without a checksum failure?
- Does every retry receive a fresh session and a complete transaction?
- Can two concurrent runners both execute after the advisory lock and metadata
  re-check?
- Are data values always outside SQL text?
- Does a lost commit response remain safe to retry?
- Do logs contain request and migration IDs without URLs, parameters, payloads,
  or raw exception messages?
- Are metric tags bounded?
- Can the service be live but not ready?
- Does incomplete recovery evidence pause instead of guessing?
- Is the live path impossible to point at a differently named database?

## Common pitfalls

- **Editing an applied migration:** history no longer explains database state.
  Add a new forward migration.
- **Checking metadata before acquiring the lock:** two runners can both see
  “pending.” Re-check inside the serialized transaction.
- **Retrying one failed statement:** PostgreSQL leaves the transaction aborted.
  Roll back, close, and retry the complete idempotent unit.
- **Retrying every exception:** permanent defects become slower and noisier.
- **Interpolating backfill values:** migration files are trusted code, but
  runtime values still belong in Psycopg parameters.
- **Using request IDs as metric labels:** cardinality grows forever. Keep them
  in structured logs.
- **Logging exception text:** driver messages may include SQL, data, or
  connection details. Record a safe type and retain protected diagnostics under
  an explicit policy.
- **Applying migrations in readiness:** probes must observe state, not mutate it.
- **Assuming rollback is safer:** reverse DDL or a previous application can be
  destructive after new-shape writes.
- **Testing with SQLite:** it does not reproduce PostgreSQL DDL transactions,
  SQLSTATEs, locks, or Psycopg binding.

## Next step

Complete the [learner file](../lessons/bridge_ops_01_migration_observability.py)
and fake-backed tests before reviewing the
[reference implementation](../solutions/bridge_ops_01_migration_observability_solution.py)
and [solution reasoning](../solutions/bridge_ops_01_migration_observability_solutions.md).
Then pair this delivery lab with the PostgreSQL migration foundation and a
small application compatibility test.
