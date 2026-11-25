# SQL-TEMPORAL-01: Temporal and Domain Modelling

## How to run this lesson

Start **sql-temporal-01** from `./classroom` using the shared [run steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Choose **Whole SQL lesson (psql)**. The script opens one transaction on
`advanced_sql_training`, builds `pro_temporal_lab` and uses fixed timestamps,
so its output does not depend on today's date. It records three term versions
for customer `CUS-100`, two adjacent maintenance windows, a two-entry change
ledger and three retained records. Four `NOTICE` lines are intended: an
overlapping current term is rejected, and the ledger refuses an update, a
delete and a duplicate idempotency key. The final check requires exactly one
term for February 15 as known on March 15 and exactly 2 ledger entries;
`ROLLBACK` then removes the schema. The script reads `pg_available_extensions`
for `btree_gist` but never enables it. Save attempts in
`.learning/sql/sql-temporal-01/lesson/workspace/sql/professional/lessons/sql_temporal_01_domain_modelling.sql`.

The optional notebook route starts with `uv run --no-sync python scripts/course.py sql notebook sql-temporal-01`; see the [study guide](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

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

## A beginner's mental model for this lesson

A temporal table keeps more than one version of a fact and says when each
version applies. This lesson uses two clocks: valid time is when the rate
applied to the customer, and system time is when the database knew it. Every
period is half-open, `[lower, upper)`, so one period can end exactly where the
next begins without overlapping. The vocabulary below (valid time, system time,
bitemporal, as-of query, half-open interval, exclusion constraint) names those
ideas.

One `customer_terms` row is one recorded version of one customer's rate for one
valid period. An as-of query fixes one valid date and one system instant and
must return at most one row for each customer; the self-check proves that for
February 15 as known March 15. One `change_ledger` row is one appended event,
and a correction is a new row that points at the entry it reverses. The
retention report returns one row per retained record.

`CUS-100` starts at a rate of 10 for January through March, recorded March 1.
On March 10 the system period of that row is closed and a corrected row at 12
is appended, together with a rate of 15 for April through June. So February 15
as known on March 5 returns 10, and as known on March 15 returns 12. No row is
overwritten: history is closed and appended. The other parts follow the same
rule. The ledger's `credit.reversed` entry cancels `LEDGER-100` instead of
editing it, and the retention report on March 15 marks only `REC-100` as
eligible for review: `REC-101` is on legal hold and `REC-102` has a 365-day
minimum.

## Two worked SQL examples

Example 1 defines the term-version table and Example 2 records its first
version.

### Example 1

```sql
CREATE TABLE pro_temporal_lab.customer_terms (
  term_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_key text NOT NULL,
  valid_period daterange NOT NULL CHECK (NOT isempty(valid_period) AND lower_inc(valid_period) AND NOT upper_inc(valid_period)),
  system_period tstzrange NOT NULL CHECK (NOT isempty(system_period) AND lower_inc(system_period) AND NOT upper_inc(system_period)),
  monthly_rate numeric(10, 2) NOT NULL CHECK (monthly_rate >= 0),
  recorded_reason text NOT NULL CHECK (btrim(recorded_reason) <> '')
);
```

**How to read it:** Both periods are ranges, and each `CHECK` requires a
non-empty range with an inclusive lower bound and an exclusive upper bound, so
every row is half-open. There is no overlap constraint here; the trigger
`prevent_current_term_overlap` adds that rule for current rows only.

**Expected result/shape:** `CREATE TABLE`. The later DO block proves the
trigger works: a second current term for `CUS-100` that overlaps an existing
one fails with `exclusion_violation`, reported as a `NOTICE`.

### Example 2

```sql
INSERT INTO pro_temporal_lab.customer_terms (customer_key, valid_period, system_period, monthly_rate, recorded_reason)
  VALUES ('CUS-100', daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'), tstzrange(TIMESTAMPTZ '2026-03-01 00:00:00+00', NULL, '[)'), 10.00, 'initial import');
```

**How to read it:** `daterange(..., '[)')` makes January 1 through March 31
valid, with April 1 excluded. `tstzrange(..., NULL, '[)')` leaves the system
period open, so the row stays current until a later correction closes it.

**Expected result/shape:** `INSERT 0 1`. After the March 10 correction this row
is still in the table, with its system period ending at
`2026-03-10 00:00:00+00`.

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

```sql fragment
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
   **Inputs/evidence:** For sql-temporal-01 Exercise 1, Close only the current `CUS-100` row whose `valid_period` contains `2026-02-15` at system time `2026-04-01 00:00+00`, then append the corrected rate as a new current `pro_temporal_lab.customer_terms` row.
   **Expected result/shape:** For sql-temporal-01 Exercise 1, One row per `(valid_on, system_as_of)` probe, with `valid_on`, `system_as_of`, `term_version_id`, `monthly_rate`, and `recorded_reason`, ordered by `system_as_of`; March 15 returns the prior rate and April 2 returns the retroactive correction.
   **Verify:** For sql-temporal-01 Exercise 1, Group the as-of join by both probe columns and require exactly one match per probe. Prove the earlier system-period row still exists and that no current valid periods overlap for `CUS-100`.
2. **Range boundaries:** test every upper endpoint and require at most one row.
   **Inputs/evidence:** For sql-temporal-01 Exercise 2, Build an inline probe relation around every lower and upper bound in `pro_temporal_lab.customer_terms`: immediately before, exactly at, and immediately after each valid-date or system-time boundary.
   **Expected result/shape:** For sql-temporal-01 Exercise 2, One row per `probe_id`, with `valid_on`, `known_at`, `matching_versions`, and `expected_matches`, ordered by `probe_id`; no `matching_versions` value is greater than one.
   **Verify:** For sql-temporal-01 Exercise 2, Independently count matching `term_version_id` values for every probe. Require the old version to stop at the upper bound and an adjacent successor, when present, to begin there without a double match.
3. **Overlap enforcement:** compare an optional exclusion constraint with the
   locking trigger fallback.
   **Inputs/evidence:** For sql-temporal-01 Exercise 3, Use the read-only `pg_available_extensions` result, the existing advisory-lock trigger, and a written (not executed) `btree_gist` exclusion constraint design for `customer_key WITH =, valid_period WITH &&`.
   **Expected result/shape:** For sql-temporal-01 Exercise 3, One comparison row per enforcement approach, with `approach`, `enforcement_mechanism`, `assumption_or_limit`, and `concurrent_failure_behavior`.
   **Verify:** For sql-temporal-01 Exercise 3, The comparison output records which writes each approach locks or constrains, how a conflicting concurrent transaction fails, and what happens if an application writer bypasses the agreed advisory-lock protocol.
4. **Ledger reversal:** append rather than update and verify idempotency and
   reversal links.
   **Inputs/evidence:** For sql-temporal-01 Exercise 4, Append `LEDGER-102` to `pro_temporal_lab.change_ledger` as the exact same-subject, same-currency negation of `LEDGER-101`; set `reverses_entry_id` from the referenced row instead of hard-coding it.
   **Expected result/shape:** For sql-temporal-01 Exercise 4, One row per `ledger_entry_id`, with `idempotency_key`, `event_kind`, signed amount, `reverses_entry_id`, and a scalar reconciled amount, ordered by `ledger_entry_id`.
   **Verify:** For sql-temporal-01 Exercise 4, Require three rows and a reconciled amount of `5.00`. Prove an UPDATE, DELETE, duplicate `LEDGER-102` retry, second reversal of the same entry, and wrong-sign reversal all fail without changing the row count.
5. **Retention decision:** preserve approver, reason, time, hold, and immutable
   audit without deleting fixtures.
   **Inputs/evidence:** For sql-temporal-01 Exercise 5, Create append-only `pro_temporal_lab.retention_decisions` with a stable decision idempotency key, `record_key`, decision, approver, reason, and authoritative `decided_at`. Lock per record and reject backdated decisions or a deletion approval while the latest decision is a hold.
   **Expected result/shape:** For sql-temporal-01 Exercise 5, One row per retained `record_key`, with the latest decision event/key, approver, reason, decision time, and `eligible_for_deletion_review`, ordered by `record_key`.
   **Verify:** For sql-temporal-01 Exercise 5, Prove decision UPDATE/DELETE and duplicate/backdated appends fail. Keep a held fixture ineligible, release another through an ordered event, and confirm no `retained_records` row is actually deleted.
6. **Assumption register:** document time, authority, lateness, gaps/overlaps,
   privacy/deletion, ledger meaning, and correction roles.
   **Inputs/evidence:** For sql-temporal-01 Exercise 6, Use observed lesson behavior plus explicitly labeled assumptions for time zone, clock authority, lateness, overlap/gaps, correction authority, ledger units, retention/holds, and replicas/backups.
   **Expected result/shape:** For sql-temporal-01 Exercise 6, One row per assumption topic, with `topic`, `decision_or_assumption`, `evidence`, `owner`, and `failure_response`.
   **Verify:** For sql-temporal-01 Exercise 6, Every row names an accountable owner and an operational response; every claimed fact cites a query/catalog result, while policy not present in the repository is labeled as an assumption needing approval.
7. **Civil time:** test ambiguous/nonexistent DST times while retaining source
   zone and UTC instant.
   **Inputs/evidence:** For sql-temporal-01 Exercise 7, Use three keyed civil-time cases in `America/Los_Angeles`: spring `2026-03-08 02:30`, fall `2026-11-01 01:30`, and one ordinary time. Round-trip candidate UTC instants rather than trusting one silent `AT TIME ZONE` default.
   **Expected result/shape:** For sql-temporal-01 Exercise 7, One row per `case_id`, with `local_time`, `zone_name`, `civil_time_status`, candidate instants, PostgreSQL's default interpreted instant, and `resolution_policy`, ordered by `case_id`.
   **Verify:** For sql-temporal-01 Exercise 7, The result contains exactly one `nonexistent`, one `ambiguous`, and one `ordinary` case. A nonexistent time has zero round-trip candidates; an ambiguous time has more than one and requires explicit disambiguation.
8. **Three clocks:** separate event, ingestion, and processing time; define
   watermark, lateness, correction, and notification.
   **Inputs/evidence:** For sql-temporal-01 Exercise 8, Create `pro_temporal_lab.timed_events(event_key, event_at, ingested_at, processed_at)` with one on-time and one late event. Use a fixed 15-minute example lateness allowance.
   **Expected result/shape:** For sql-temporal-01 Exercise 8, Exactly one summary row with `event_count`, `maximum_event_time`, `example_watermark`, `maximum_arrival_delay`, `maximum_processing_delay`, `events_behind_watermark`, and the correction policy.
   **Verify:** For sql-temporal-01 Exercise 8, Recompute arrival and processing delays row by row, require the late fixture to fall behind the watermark, and describe a stable window/version identity for the corrected aggregate.
9. **Type-2 join:** use business/surrogate keys and half-open effective periods;
   require at most one match per fact.
   **Inputs/evidence:** For sql-temporal-01 Exercise 9, Create `pro_temporal_lab.customer_dimension` with surrogate `customer_version_id`, business key, half-open `effective_period`, `is_current`, segment, correction reason, and record time; join `pro_temporal_lab.order_facts` on business key plus range containment.
   **Expected result/shape:** For sql-temporal-01 Exercise 9, One row per `order_key`, with `ordered_on`, `customer_version_id`, segment, effective period, current marker, and correction metadata, ordered by `order_key`.
   **Verify:** For sql-temporal-01 Exercise 9, Require output count to equal fact count and group by `order_key` with `HAVING count(customer_version_id) > 1` returning no rows. Inject one overlapping dimension row, prove the diagnostic catches it, then roll it back.
10. **Temporal parent:** design period containment, concurrency protection,
    deferred checking, and repair.
   **Inputs/evidence:** For sql-temporal-01 Exercise 10, Cover child insert/update, parent shrink/delete, bulk historical repair, and deferred validation. State the shared business-key locking namespace and containment predicate for each write path.
   **Expected result/shape:** For sql-temporal-01 Exercise 10, One row per write path, with `write_path`, `concurrency_or_validation_control`, and `failure_response`.
   **Verify:** For sql-temporal-01 Exercise 10, Walk through two concurrent transactions for both child insertion and parent shrink. Identify the lock acquired first and show that cutover is blocked whenever the final containment diagnostic is nonempty.
11. **Gap/overlap report:** use deterministic window/multirange logic and define
    adjacency, duplicates, and empty periods.
   **Inputs/evidence:** For sql-temporal-01 Exercise 11, Use keyed fixtures containing duplicate, overlapping, adjacent, gapped, empty, and unbounded-upper `daterange` values. Preserve unbounded prior coverage with `upper_inf()` or an explicit infinity sentinel.
   **Expected result/shape:** For sql-temporal-01 Exercise 11, One row per `period_id`, with `business_key`, `valid_period`, `has_unbounded_upper`, duplicate count, prior maximum upper bound, and `relationship_to_prior_coverage`, ordered by bounds and `period_id`.
   **Verify:** For sql-temporal-01 Exercise 11, Require explicit `duplicate`, `empty`, `gap`, `adjacent`, and `overlap` outcomes. Add a bounded period after an unbounded range and prove it is classified as overlap rather than first/gap.
12. **Archival:** plan partition detach, legal-hold exceptions, verification,
    protected storage, restore tests, and deletion proof.
   **Inputs/evidence:** For sql-temporal-01 Exercise 12, Design ordered phases for inventory, hold gate, detach, encrypted archive, reconciliation, restore test, and eventual source deletion.
   **Expected result/shape:** For sql-temporal-01 Exercise 12, One row per `step_number`, with `phase`, `required_control`, and `required_evidence`, ordered by `step_number`.
   **Verify:** For sql-temporal-01 Exercise 12, Each phase names a stop condition. Trace one active-hold fixture through every maintained copy and require a successful isolated restore plus source/archive count and checksum reconciliation before deletion.

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

## Ask an AI tutor about this lesson

The lesson and expected observations are sufficient offline. For optional
coaching, copy:

```text
Tutor me through sql-temporal-01: Temporal Data and Domain Modelling.

I have completed the direct catalog prerequisites: `sql-found-01`, `sql-types-01`, `sql-prog-01`, `sql-test-01`, `sql-39`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_temporal_01_domain_modelling.md
- Answer-free learner SQL: sql/professional/lessons/sql_temporal_01_domain_modelling.sql

Key terms to teach in context: Valid time, System time, Bitemporal, As-of query, Half-open interval, Exclusion constraint. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The term-version grain is one recorded version of one customer's fact. A February-valid rate first enters the system March 1. On March 10, the old system period is closed and a corrected row begins. Querying valid February 15 as known March 5 returns 10; as known March 15 returns 12. History is appended/closed, not overwritten.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
