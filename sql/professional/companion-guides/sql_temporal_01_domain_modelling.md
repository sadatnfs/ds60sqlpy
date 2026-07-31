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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-temporal-01/lesson/workspace/sql/professional/lessons/sql_temporal_01_domain_modelling.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is Valid time, System time, Bitemporal, As-of query, Half-open interval, Exclusion constraint. Its worked SQL reads or creates `pro_temporal_lab.customer_terms`, `pro_temporal_lab.global_maintenance_windows`, `pg_catalog.pg_available_extensions`, `pro_temporal_lab.change_ledger`, `pro_temporal_lab.retention_classes`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: The term-version grain is one recorded version of one customer's fact. A February-valid rate first enters the system March 1. On March 10, the old system period is closed and a corrected row begins. Querying valid February 15 as known March 5 returns 10; as known March 15 returns 12. History is appended/closed, not overwritten.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `pro_temporal_lab.customer_terms`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

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

**Expected result/shape:** Example 1 must print the expected DDL command tag for `pro_temporal_lab.customer_terms`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

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

**Expected result/shape:** Example 2 must complete through `psql` with its documented command tag or notice for `pro_temporal_lab.customer_terms`. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup.

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
   **Inputs/evidence:** For sql-temporal-01 Exercise 1, complete the retroactive correction written analysis and support its claims with read-only evidence from `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-temporal-01 Exercise 1, expected output: a completed the retroactive correction written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
   **Verify:** For sql-temporal-01 Exercise 1, check the retroactive correction written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
2. **Range boundaries:** test every upper endpoint and require at most one row.
   **Inputs/evidence:** For sql-temporal-01 Exercise 2, read from `pro_temporal_lab.facts`. Build the answer toward `valid_on`, `known_at`, and `matching_versions`; keep `valid_on`, and `known_at` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-temporal-01 Exercise 2, expected output: one row per `valid_on`, and `known_at`. The final columns are `valid_on`, `known_at`, and `matching_versions`. The final order is `probe.valid_on`.
   **Verify:** For sql-temporal-01 Exercise 2, independently aggregate `pro_temporal_lab.facts` by `valid_on`, and `known_at`; require one output row for every distinct `valid_on`, and `known_at` tuple and compare `matching_versions` tuple by tuple. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
3. **Overlap enforcement:** compare an optional exclusion constraint with the
   locking trigger fallback.
   **Inputs/evidence:** For sql-temporal-01 Exercise 3, complete the overlap enforcement written analysis and support its claims with read-only evidence from `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-temporal-01 Exercise 3, expected output: a completed the overlap enforcement written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `btree_gist`, `customer_key`, and `valid_period`.
   **Verify:** For sql-temporal-01 Exercise 3, check the overlap enforcement written analysis against `btree_gist`, `customer_key`, and `valid_period`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
4. **Ledger reversal:** append rather than update and verify idempotency and
   reversal links.
   **Inputs/evidence:** For sql-temporal-01 Exercise 4, read the target keys from `pro_temporal_lab.ledger` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-temporal-01 Exercise 4, expected output: the command tag and an independently counted set of affected `entry_id` values. The final columns are `entry_id`. The final order is `l.entry_id`.
   **Verify:** For sql-temporal-01 Exercise 4, materialize the intended `entry_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_temporal_lab.ledger` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `entry_id` values in both cases.
5. **Retention decision:** preserve approver, reason, time, hold, and immutable
   audit without deleting fixtures.
   **Inputs/evidence:** For sql-temporal-01 Exercise 5, read the target keys from `pro_temporal_lab.retention_decisions`, `pro_temporal_lab.facts`, and `pro_temporal_lab.ledger` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-temporal-01 Exercise 5, expected output: the command tag and an independently counted set of affected `affected_row_count` values. The final columns are `affected_row_count`, and `command_tag`.
   **Verify:** For sql-temporal-01 Exercise 5, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_temporal_lab.retention_decisions`, `pro_temporal_lab.facts`, and `pro_temporal_lab.ledger` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
6. **Assumption register:** document time, authority, lateness, gaps/overlaps,
   privacy/deletion, ledger meaning, and correction roles.
   **Inputs/evidence:** For sql-temporal-01 Exercise 6, complete the assumption register written analysis and support its claims with read-only evidence from `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-temporal-01 Exercise 6, expected output: a completed the assumption register written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
   **Verify:** For sql-temporal-01 Exercise 6, check the assumption register written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
7. **Civil time:** test ambiguous/nonexistent DST times while retaining source
   zone and UTC instant.
   **Inputs/evidence:** For sql-temporal-01 Exercise 7, read from the inline `VALUES` fixture. Build the answer toward `local_time`, `zone_name`, and `interpreted_instant`; keep `zone_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-temporal-01 Exercise 7, expected output: one row per `zone_name`. The final columns are `local_time`, `zone_name`, and `interpreted_instant`. The final order is `local_time`.
   **Verify:** For sql-temporal-01 Exercise 7, reselect the returned keys directly from the source; require unique `zone_name` where the expected grain is one row per key and confirm the projected `local_time`, `zone_name`, and `interpreted_instant` against the inline `VALUES` fixture. Add one source row with a new `zone_name`; verify the result gains exactly one row carrying that `zone_name` value.
8. **Three clocks:** separate event, ingestion, and processing time; define
   watermark, lateness, correction, and notification.
   **Inputs/evidence:** For sql-temporal-01 Exercise 8, read from `pro_temporal_lab.timed_events`. Build the answer toward `maximum_event_time`, `example_watermark`, and `maximum_arrival_delay`; keep `example_watermark` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-temporal-01 Exercise 8, expected output: one row per `example_watermark`. The final columns are `maximum_event_time`, `example_watermark`, and `maximum_arrival_delay`.
   **Verify:** For sql-temporal-01 Exercise 8, reselect the returned keys directly from the source; require unique `example_watermark` where the expected grain is one row per key and confirm the projected `maximum_event_time`, `example_watermark`, and `maximum_arrival_delay` against `pro_temporal_lab.timed_events`. Add one source row with a new `example_watermark`; verify the result gains exactly one row carrying that `example_watermark` value.
9. **Type-2 join:** use business/surrogate keys and half-open effective periods;
   require at most one match per fact.
   **Inputs/evidence:** For sql-temporal-01 Exercise 9, read from `pro_temporal_lab.customer_dimension`. Build the answer toward `order_key`, `ordered_on`, `customer_version_id`, and `segment`; keep `customer_version_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-temporal-01 Exercise 9, expected output: one row per `customer_version_id`. The final columns are `order_key`, `ordered_on`, `customer_version_id`, and `segment`. The final order is `order_fact.order_key`.
   **Verify:** For sql-temporal-01 Exercise 9, project `customer_version_id` plus the raw source columns from `pro_temporal_lab.customer_dimension` at each join stage; record row count and distinct `customer_version_id`, then assert the final `order_key`, `ordered_on`, `customer_version_id`, and `segment` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
10. **Temporal parent:** design period containment, concurrency protection,
    deferred checking, and repair.
   **Inputs/evidence:** For sql-temporal-01 Exercise 10, complete the temporal parent written analysis and support its claims with read-only evidence from `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-temporal-01 Exercise 10, expected output: a completed the temporal parent written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
   **Verify:** For sql-temporal-01 Exercise 10, check the temporal parent written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
11. **Gap/overlap report:** use deterministic window/multirange logic and define
    adjacency, duplicates, and empty periods.
   **Inputs/evidence:** For sql-temporal-01 Exercise 11, read from `periods`. Build the answer toward `period_id`, `valid_period`, and `relationship_to_prior_coverage`; keep `period_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-temporal-01 Exercise 11, expected output: one row per `period_id`. The final columns are `period_id`, `valid_period`, and `relationship_to_prior_coverage`. The final order is `lower(w.valid_period), upper(w.valid_period), w.period_id`.
   **Verify:** For sql-temporal-01 Exercise 11, reselect the returned keys directly from the source; require unique `period_id` where the expected grain is one row per key and confirm the projected `period_id`, `valid_period`, and `relationship_to_prior_coverage` against `periods`. Add duplicate source candidates for `period_id`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
12. **Archival:** plan partition detach, legal-hold exceptions, verification,
    protected storage, restore tests, and deletion proof.
   **Inputs/evidence:** For sql-temporal-01 Exercise 12, use `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-temporal-01 Exercise 12, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
   **Verify:** For sql-temporal-01 Exercise 12, restore into an isolated target and reconcile `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

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

I have completed the direct catalog prerequisites: `sql-found-01`, `sql-types-01`, `sql-prog-01`, `sql-test-01`, `sql-39`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_temporal_01_domain_modelling.md
- Answer-free learner SQL: sql/professional/lessons/sql_temporal_01_domain_modelling.sql

Key terms to teach in context: Valid time, System time, Bitemporal, As-of query, Half-open interval, Exclusion constraint. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The term-version grain is one recorded version of one customer's fact. A February-valid rate first enters the system March 1. On March 10, the old system period is closed and a corrected row begins. Querying valid February 15 as known March 5 returns 10; as known March 15 returns 12. History is appended/closed, not overwritten.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-temporal-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
