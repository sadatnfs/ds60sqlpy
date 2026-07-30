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
            "UPDATE training.bridge_release_lab SET source_label = %s WHERE source_label IS NULL",
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

### Practice contract

- **Focus:** Deliver immutable ordered PostgreSQL migrations with fake-tested retry/commit uncertainty, redacted observability, readiness probes, and evidence-driven recovery.
- **Assumptions:** Each migration has stable identity/content/checksum; every attempt owns a fresh transaction; optional live work targets only the disposable course database.
- **Primary failure mode:** Mutable history, retry after uncertain commit without re-checking metadata, or recovery without complete evidence can corrupt schema state.
- **Evidence loop:** state the boundary and prediction, implement against
  deterministic local doubles, test success/failure/cleanup, and label any
  optional live-adapter evidence separately from offline proof.

1. **Validation:** Implement `Migration` validation and a stable checksum over identity,
   description, command text/parameters, and verification.
   - **Progressive hint:** Canonical serialization must distinguish structure and parameter
     types without depending on object repr.
2. **Redaction:** Implement `redact_fields()` for sensitive key names, URL-shaped values,
   non-serializable objects, and ordinary scalars.
   - **Progressive hint:** Use key classification and safe type conversion; never echo rejected
     values.
3. **Planning:** Implement `plan_pending()` with duplicate/order validation, unknown
   applied-version rejection, and checksum-drift detection.
   - **Progressive hint:** Applied history is immutable and must be a prefix of known ordered
     migrations.
4. **Test double:** Build a recording session fake that stores SQL separately from parameter
   tuples and never parses PostgreSQL through SQLite.
   - **Progressive hint:** Model transactional state and prepared query results explicitly.
5. **Delivery:** Implement the documented nine-step delivery order and prove rollback/close
   happen before injected retry delay.
   - **Progressive hint:** One attempt must acquire, lock, re-check, apply, verify, record,
     commit, close, then report.
6. **Commit uncertainty:** Simulate an uncertain commit whose retry sees a matching metadata row
   and prove commands are not applied twice.
   - **Progressive hint:** Re-check immutable metadata under lock before every attempt.
7. **Observability:** Add event and metric fakes; require request/migration IDs in logs, exclude
   request IDs from metric tags, and prove secrets are absent.
   - **Progressive hint:** Logs support correlation; metrics require bounded dimensions.
8. **Readiness:** Implement read-only readiness for current, pending, drifted, and unreachable
   states while keeping liveness database-independent.
   - **Progressive hint:** Readiness describes safe traffic acceptance, not process existence.
9. **Recovery:** Build a scenario table for recovery decisions, including incomplete evidence
   that must pause.
   - **Progressive hint:** Destructive or forward actions require rehearsed, compatible
     evidence.
10. **Optional integration:** After fake tests, run the disposable live lab twice and inspect
   migration metadata with a read-only query.
   - **Progressive hint:** The second run demonstrates idempotency; cleanup evidence is part of
     completion.
11. **Immutability:** Change only SQL whitespace after a migration is applied and decide whether
   checksum drift should be accepted.
   - **Progressive hint:** A stored checksum is an immutable history contract, not a semantic
     SQL parser.
12. **Concurrency:** Model two deployers contending for the same advisory lock and specify
   timeout/ownership behavior.
   - **Progressive hint:** Only one delivery transaction may make planning decisions at a time.
13. **PostgreSQL semantics:** Identify which DDL is transactional in PostgreSQL and how
   non-transactional commands alter the migration policy.
   - **Progressive hint:** Do not assume every administrative statement can share ordinary
     transaction rollback.
14. **Timeouts:** Set statement and lock timeouts per attempt without leaking settings to later
   pooled work.
   - **Progressive hint:** Transaction-local settings should expire with commit/rollback.
15. **Telemetry design:** Define a bounded migration metric schema and a redaction test for
   exception objects and URL-like fields.
   - **Progressive hint:** Migration IDs may still become unbounded over years; choose
     dimensions deliberately.
16. **Probe semantics:** Distinguish current-but-stale application readiness from database
   reachability and migration currency.
   - **Progressive hint:** Each probe should answer one operational question.
17. **Decision analysis:** Compare forward fix and release rollback when the new schema has
   already received writes.
   - **Progressive hint:** Data written under the new contract can make old code incompatible
     even if DDL reversal is possible.
18. **Expand-contract:** Design a three-release expand/migrate/contract sequence for renaming a
   populated column.
   - **Progressive hint:** Maintain compatibility while old and new application versions
     overlap.
19. **Cleanup:** Prove the optional live lab leaves no table, metadata row, lock, connection, or
   credential-bearing output behind.
   - **Progressive hint:** A passing mutation test is incomplete without postconditions.
20. **Failure simulation:** Inject a network-like error immediately after fake commit and
   require the retry to gather evidence rather than blindly replay.
   - **Progressive hint:** Client exceptions after commit do not prove server rollback.

### Before opening the solution

- Record what the offline doubles prove and what they cannot prove.
- Inspect exact call order, parameters, schema, and failure behavior.
- Keep credentials, payloads, and high-cardinality identifiers out of output.
- Require deterministic reruns before considering an exercise complete.


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
