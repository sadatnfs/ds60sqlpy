# SQL-TEMPORAL-01 — Temporal and Domain Modelling

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-found-01`, `sql-types-01`, `sql-prog-01`,
  `sql-test-01`, and `sql-39`
- **Prerequisites:** [SQL-FOUND-01](sql_found_01_relational_design.md),
  [SQL-TYPES-01](sql_types_01_native_types_search.md),
  [SQL-PROG-01](sql_prog_01_routines_triggers.md),
  [SQL-TEST-01](sql_test_01_contracts_migrations.md), ranges, triggers, and
  [SQL Day 39 transaction/advisory-lock concepts](../../postgres-60day/companion-guides/day39_locks_deadlocks.md).
- **Artifacts:** [learner SQL](../lessons/sql_temporal_01_domain_modelling.sql) ·
  [solution reasoning](../solutions/sql_temporal_01_domain_modelling_solutions.md) ·
  [executable solution](../solutions/sql_temporal_01_domain_modelling_solutions.sql)

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_temporal_01_domain_modelling.sql
```

The default is offline, fixed-time, and rollback-safe. It inspects but never
enables `btree_gist`.

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-TEMPORAL-01 — Temporal and Domain Modelling** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-temporal-01/sql_temporal_01_domain_modelling.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_temporal_01_domain_modelling.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_temporal_01_domain_modelling.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. This lesson introduces or reinforces
Valid time, System time, Bitemporal, As-of query, Half-open interval, Exclusion constraint. Its worked SQL reads or creates `pro_temporal_lab.customer_terms`, `pro_temporal_lab.global_maintenance_windows`, `pg_catalog.pg_available_extensions`, `pro_temporal_lab.change_ledger`, `pro_temporal_lab.retention_classes`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: The term-version grain is one recorded version of one customer's fact. A February-valid rate first enters the system March 1. On March 10, the old system period is closed and a corrected row begins. Querying valid February 15 as known March 5 returns 10; as known March 15 returns 12. History is appended/closed, not overwritten.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_temporal_01_domain_modelling.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE pro_temporal_lab.customer_terms (
    term_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_key text NOT NULL,
    valid_period daterange NOT NULL CHECK (
        NOT isempty(valid_period)
        AND lower_inc(valid_period)
        AND NOT upper_inc(valid_period)
    ),
    system_period tstzrange NOT NULL CHECK (
        NOT isempty(system_period)
        AND lower_inc(system_period)
        AND NOT upper_inc(system_period)
    ),
    monthly_rate numeric(10, 2) NOT NULL CHECK (monthly_rate >= 0),
    recorded_reason text NOT NULL CHECK (btrim(recorded_reason) <> '')
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
INSERT INTO pro_temporal_lab.customer_terms (
    customer_key,
    valid_period,
    system_period,
    monthly_rate,
    recorded_reason
)
VALUES (
    'CUS-100',
    daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'),
    tstzrange(TIMESTAMPTZ '2026-03-01 00:00:00+00', NULL, '[)'),
    10.00,
    'initial import'
);
```

**How to read it:** Example 2 changes rows inside the lesson's declared transaction. The command tag reports affected rows, but a follow-up query must prove the intended before/after invariant.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Distinguish valid and system time and query bitemporal state as-of two clocks.
- Enforce half-open non-overlap and compare built-in/advisory with exclusion
  constraints.
- Model an append-only correction ledger and produce legal-hold-aware retention
  eligibility without silently deleting evidence.

## Vocabulary and concepts

- **Valid time:** when a fact is true in the modeled domain.
- **System time:** when the database recorded/believed that version.
- **Bitemporal:** tracks both valid and system intervals.
- **As-of query:** asks state at a chosen valid and/or system instant.
- **Half-open interval:** `[lower,upper)`, avoiding double membership at adjacent
  boundaries.
- **Exclusion constraint:** prevents rows whose indexed operators conflict.
- **Ledger:** append-only record where correction uses reversal/new entries.
- **Idempotency key:** stable uniqueness key preventing duplicate append.
- **Retention class:** approved minimum duration and policy basis.
- **Legal hold:** policy override preventing eligible deletion.

## Worked example / walkthrough

The term-version grain is one recorded version of one customer's fact. A
February-valid rate first enters the system March 1. On March 10, the old system
period is closed and a corrected row begins. Querying valid February 15 as known
March 5 returns 10; as known March 15 returns 12. History is appended/closed,
not overwritten.

Both periods use `[lower,upper)`. Adjacent valid terms ending/starting April 1
do not overlap. NULL upper system bound means currently believed. Production
models must define clock source, time zone, late arrival, whether valid gaps are
allowed, and who may correct history.

Per-key exclusion normally uses `btree_gist`:

```sql
-- Optional, only after btree_gist is approved and installed:
EXCLUDE USING gist (
    customer_key WITH =,
    valid_period WITH &&
) WHERE (upper_inf(system_period))
```

The default does not enable the extension. Its trigger obtains a transaction
advisory lock derived from customer key, then rejects overlaps among current
system rows. The lock closes a common concurrent check-then-insert race, though
hash collisions can serialize unrelated keys. Declarative exclusion is easier
to inspect and harder to bypass; either design needs migration/concurrency tests.

A global maintenance table demonstrates built-in range-only GiST exclusion.
Adjacent windows succeed while overlap would fail.

The change ledger rejects UPDATE/DELETE. A correction appends a reversal with
unique idempotency key and reference to the original. Append-only does not prove
truth or authorization; ownership, signing/tamper controls, reconciliations, and
retention still matter.

Retention rules are data with policy basis. The query produces candidates at a
fixed review timestamp and excludes legal holds. It does not delete. Actual
deletion/anonymization requires approved scope, referential impact, audit,
backup-copy handling, dry run, and bounded recoverability.

## Exercises

Complete all twelve prompts. Begin with retroactive bitemporal correction, boundary tests,
optional exclusion design, ledger reversal, held-retention workflow, and an
explicit domain-assumption record; then cover civil time, three clocks, Type-2
joins, temporal parents, gaps/overlaps, and hold-aware archival. Add negative
controls for overlap, mutation, duplicate idempotency, and held deletion.

For every temporal answer, name the clock, zone, lower/upper inclusivity,
late-arrival policy, overlap/gap rule, correction authority, and audit evidence:

1. **Retroactive correction:** compare valid-at/known-at answers before and
   after the recorded correction.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
2. **Range boundaries:** test every upper endpoint and require at most one row.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Overlap enforcement:** compare an optional exclusion constraint with the
   locking trigger fallback.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
4. **Ledger reversal:** append rather than update and verify idempotency and
   reversal links.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. **Retention decision:** preserve approver, reason, time, hold, and immutable
   audit without deleting fixtures.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
6. **Assumption register:** document time, authority, lateness, gaps/overlaps,
   privacy/deletion, ledger meaning, and correction roles.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. **Civil time:** test ambiguous/nonexistent DST times while retaining source
   zone and UTC instant.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
8. **Three clocks:** separate event, ingestion, and processing time; define
   watermark, lateness, correction, and notification.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
9. **Type-2 join:** use business/surrogate keys and half-open effective periods;
   require at most one match per fact.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
10. **Temporal parent:** design period containment, concurrency protection,
    deferred checking, and repair.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
11. **Gap/overlap report:** use deterministic window/multirange logic and define
    adjacency, duplicates, and empty periods.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
12. **Archival:** plan partition detach, legal-hold exceptions, verification,
    protected storage, restore tests, and deletion proof.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

## Self-check

- Can the same valid date return different facts at different system times?
- Does every adjacent upper boundary match at most one row?
- Is per-key overlap safe under concurrent writers?
- Is history corrected by append/close rather than overwrite?
- Are ledger idempotency and reversal references enforced?
- Is retention eligibility separate from destructive execution?
- Do legal hold and policy basis appear in evidence?
- Does rollback remove schema, triggers, locks, and fixture data?

## Common pitfalls

- One `updated_at` timestamp is not bitemporal history.
- Inclusive upper bounds double-count adjacent periods.
- `LIMIT 1` hides overlapping history instead of enforcing it.
- A trigger overlap check without serialization races under concurrency.
- System time based on application clocks can arrive out of order.
- Append-only data can still contain false/unauthorized events.
- Retention automation without holds and backup policy can violate obligations.
- “Delete after N days” ignores referential, audit, replica, and backup copies.
- Range/exclusion indexes add write/lock cost that needs measurement.

## Next step

Use [SQL-TEST-01](sql_test_01_contracts_migrations.md) to freeze boundary,
overlap, correction, and retention contracts; use
[SQL-REPL-01](sql_repl_01_cdc_high_availability.md) to propagate immutable
versioned events idempotently; and use
[SQL-OPS-02](sql_ops_02_backup_restore_recovery.md) to rehearse recovery without
erasing required historical evidence. This completes the shared PostgreSQL
professional specialization path.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-temporal-01 — Temporal and Domain Modelling.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/professional/companion-guides/sql_temporal_01_domain_modelling.md
- Answer-free learner SQL: sql/professional/lessons/sql_temporal_01_domain_modelling.sql

The lesson concepts include Valid time, System time, Bitemporal, As-of query, Half-open interval, Exclusion constraint. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The term-version grain is one recorded version of one customer's fact. A February-valid rate first enters the system March 1. On March 10, the old system period is closed and a corrected row begins. Querying valid February 15 as known March 5 returns 10; as known March 15 returns 12. History is appended/closed, not overwritten.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-temporal-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
